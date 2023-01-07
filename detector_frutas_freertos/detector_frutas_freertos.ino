#include "embedia.h"
#include "sequential_4_model.h"
#include "semaforos.h"
#include "SerialTransfer.h"
#include "esp_camera.h"

#define PLAZO_MAXIMO_MS 800   //tareas periodicas cada este tiempo

#define TIEMPO_PAUSA_MS 1 

#define INPUT_SIZE (SEQUENTIAL_4_MODEL_CHANNELS*SEQUENTIAL_4_MODEL_WIDTH*SEQUENTIAL_4_MODEL_HEIGHT)
#define NUMBER_OF_INPUTS INPUT_SIZE //96x96x3
#define TAMANO_MAX_PAQUETE 252

#define RESOLUCION_CAMARA   FRAMESIZE_96X96          // 96x96

#define PWDN_GPIO_NUM       32
#define RESET_GPIO_NUM      -1
#define XCLK_GPIO_NUM        0
#define SIOD_GPIO_NUM       26
#define SIOC_GPIO_NUM       27

#define Y9_GPIO_NUM         35
#define Y8_GPIO_NUM         34
#define Y7_GPIO_NUM         39
#define Y6_GPIO_NUM         36
#define Y5_GPIO_NUM         21
#define Y4_GPIO_NUM         19
#define Y3_GPIO_NUM         18
#define Y2_GPIO_NUM          5
#define VSYNC_GPIO_NUM      25
#define HREF_GPIO_NUM       23
#define PCLK_GPIO_NUM       22

const TickType_t xDelay = (TIEMPO_PAUSA_MS / portTICK_PERIOD_MS); //delay en ms

//variables globales compartidas por los dos threads

SerialTransfer myTransfer;

// Structure with input data for the inference function
fixed input_data[NUMBER_OF_INPUTS];


// Structure with input data for the inference function
data_t input = { SEQUENTIAL_4_MODEL_CHANNELS, SEQUENTIAL_4_MODEL_WIDTH, SEQUENTIAL_4_MODEL_HEIGHT, input_data };


TaskHandle_t Task1;
TaskHandle_t Task2;



SemaphoreHandle_t SemBinaryA = NULL;
SemaphoreHandle_t SemBinaryB = NULL;
SemaphoreHandle_t mutex = NULL;




void setup() {

  Serial.begin(2000000);

    myTransfer.begin(Serial);

    if (myTransfer.available()){
      myTransfer.reset();
      
    }

    delay(3000);

    SemBinaryA = xSemaphoreCreateBinary();
    SemBinaryB = xSemaphoreCreateBinary();
    mutex = xSemaphoreCreateBinary();

    //Semaforo B arranca ocupado!
    
    V_a();  //liberamos semaforo A para que comience task1
    V_mutex(); //arranca liberado mutex
  
  
    xTaskCreatePinnedToCore(Task1code,"Task1",50000,NULL,1,&Task1,0);                         
  
  
    xTaskCreatePinnedToCore(Task2code,"Task2",50000,NULL,1,&Task2,1);                         



}

void Task1code( void * parameter ){ //tomar fotografia y envia la foto por serie

  //variables privadas


  
  int paquete_extra = 0;
  const int tamano_float = 2; //2 bytes
  
  uint16_t numPackets;
  uint8_t dataLen_ultimo_paquete;
  uint16_t last_index;
  uint16_t fileIndex;
  uint16_t cant_floats;
  uint8_t dataLen;

  
  uint32_t offset_canal_1 = SEQUENTIAL_4_MODEL_WIDTH*SEQUENTIAL_4_MODEL_HEIGHT;
  
  uint32_t offset_canal_2 = SEQUENTIAL_4_MODEL_WIDTH*SEQUENTIAL_4_MODEL_HEIGHT*2;

  portTickType xLastWakeTime;

    // Configuracion de la camara

    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_RGB565;
    config.frame_size = RESOLUCION_CAMARA;
    config.fb_count = 2;
    config.jpeg_quality = 0;  //best
  

  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }


  numPackets = (tamano_float*NUMBER_OF_INPUTS) / (TAMANO_MAX_PAQUETE ); 
  dataLen_ultimo_paquete=0;
  last_index = (numPackets*(TAMANO_MAX_PAQUETE/tamano_float));
  fileIndex=0;
  cant_floats = TAMANO_MAX_PAQUETE/tamano_float;
  dataLen = TAMANO_MAX_PAQUETE ;
  paquete_extra = 0;
  
  if ((tamano_float*NUMBER_OF_INPUTS) % (TAMANO_MAX_PAQUETE)){ // Add an extra transmission if needed
    paquete_extra=1;
    dataLen_ultimo_paquete=tamano_float*(NUMBER_OF_INPUTS-(last_index));
  }

  xLastWakeTime = xTaskGetTickCount();

  for(;;){


    
    P_a(); //espera en el semaforo A por mucho tiempo

    
    camera_fb_t * fb = NULL;
  
    fb = esp_camera_fb_get(); //obtengo el puntero a la estructura
    if (!fb) {
      ESP_LOGE(TAG, "Camera capture failed");
    }
  
    uint32_t indi=0;
    uint32_t contt = 0;
  
    uint32_t maxx=18432;  //input * (2/3) 120x160x3=38400 , 96x96x3=18432

    
    
    for (indi=0;indi<maxx;indi+=2){
      char high = fb->buf[indi];
      char low = fb->buf[indi+1];
      
      
      int red = (high &  0b11111000) >> 3;
      int green = ((high & 0b00000111) << 3) + ((low & 0b11100000) >> 5);
      int blue = (low &  0b00011111);
      
      float red_f = (red * 0.064516) - 1;  //from 0 to 31 to -1 to 1
      float green_f = (green * 0.031746) - 1;  //from 0 to 63 to -1 to 1
      float blue_f = (blue * 0.064516) - 1;  //from 0 to 31 to -1 to 1
      
  
      fixed red_fixed = FL2FX(red_f);
      fixed green_fixed = FL2FX(green_f);
      fixed blue_fixed = FL2FX(blue_f);
  
      //convertir a formato ancho,alto,canal que necesita embedia
  
  
      input_data[contt] = red_fixed;
      input_data[offset_canal_1 + contt] = green_fixed;
      input_data[offset_canal_2 + contt] = blue_fixed;
  
      
      contt++;
   
     
    }

    esp_camera_fb_return(fb); //libera  la memoria reservada (fb)


    //Serial.println("task1 ya saco fotoleti");

    V_b(); //libera sem B asi pasa task2 y hace la copia de la imagen
    
    
    //mandamos paquetes enteros 
    //cuando se este usando el puerto serie para transmitir un paquete , no lo interrumpimos hasta q termine => usamos mutexs
    uint16_t i;
    if(paquete_extra==0){
      
      P_mutex();
      myTransfer.txObj(input_data[0], 0, dataLen); // Stuff the current file data
      myTransfer.sendData(dataLen, 0);  //mando primer paquete id=0
      vTaskDelay(xDelay);
      
      V_mutex();
      
      for (i=1; i<numPackets-1; i++) // Send all data within the file across multiple packets
      {
        P_mutex();
        fileIndex = i*cant_floats; // Determine the current file index
        myTransfer.txObj(input_data[fileIndex], 0, dataLen); // Stuff the current file data
        myTransfer.sendData(dataLen, 1);
        vTaskDelay(xDelay);
        V_mutex();
  
      }
      
      P_mutex();
      
      myTransfer.txObj(input_data[cant_floats*(numPackets-1)], 0, dataLen); // Stuff the current file data
      myTransfer.sendData(dataLen, 2);  //mando ultimo paquete con id=2
      vTaskDelay(xDelay);

      V_mutex();
      
  
      
    }else{

      P_mutex();
      myTransfer.txObj(input_data[0], 0, dataLen); // Stuff the current file data
      myTransfer.sendData(dataLen, 0);
      vTaskDelay(xDelay);
      V_mutex();
   
      for (i=1; i<numPackets; i++) // Send all data within the file across multiple packets
      {
        P_mutex();
        fileIndex = i*cant_floats; // Determine the current file index
        myTransfer.txObj(input_data[fileIndex], 0, dataLen); // Stuff the current file data
        myTransfer.sendData(dataLen, 1);
        vTaskDelay(xDelay);
        V_mutex();
  
      }

      P_mutex();
      myTransfer.txObj(input_data[last_index], 0, dataLen_ultimo_paquete); // Stuff the current file data
      myTransfer.sendData(dataLen_ultimo_paquete, 2); // Send the current data id=2
      vTaskDelay(xDelay);
      
      V_mutex();
    
    }
    
  //------------------- HASTA ACA TASK1 ------------------------

  vTaskDelayUntil(&xLastWakeTime,(PLAZO_MAXIMO_MS/portTICK_RATE_MS)); //periodica cada PLAZO_MAXIMO_MS ms
  
  }
  vTaskDelete(NULL);
}


void Task2code( void * parameter ){ //hace una copia de la foto original y realiza inferencia en la red, luego envia resultados por serie


  uint32_t respuesta [3];

  portTickType xLastWakeTime,time_anterior,time_ahora;


  // model initialization
    model_init();

  //time_anterior = xTaskGetTickCount();
  xLastWakeTime = xTaskGetTickCount();

  for(;;){

    P_b(); //espera en el semaforo B por mucho tiempo
    //comienzo seccion critica

    //Serial.println("taks2 ya paso el sem b");

    portTickType tiempo_inferencia = xTaskGetTickCount();
    
    // model inference
    int prediction = model_predict(input); 

    tiempo_inferencia = xTaskGetTickCount() - tiempo_inferencia;
 

    respuesta[0] = uint32_t (prediction);
    respuesta[1] = uint32_t (tiempo_inferencia);
    respuesta[2] = uint32_t (time_ahora);
    
    P_mutex();
 
    myTransfer.txObj(respuesta[0], 0, 12); // Stuff the current file data 16 bytes
    myTransfer.sendData(12, 3);  //mando con id = 3
    vTaskDelay(xDelay);

    V_mutex();
    
    //------------------- HASTA ACA TASK2 ------------------------


    vTaskDelayUntil(&xLastWakeTime,(PLAZO_MAXIMO_MS/portTICK_RATE_MS)); //periodica cada PLAZO_MAXIMO_MS ms

    time_ahora = xLastWakeTime - time_anterior;
    time_anterior = xLastWakeTime;

    
  }
  vTaskDelete(NULL);
}


  



void loop() {
  //IDLE Task do nothing....
}




void P_a(void){
  xSemaphoreTake(SemBinaryA, portMAX_DELAY);
}
void P_b(void){
  xSemaphoreTake(SemBinaryB, portMAX_DELAY);
}
void P_mutex(void){
  xSemaphoreTake(mutex, portMAX_DELAY);
}
void V_a(void){
  xSemaphoreGive(SemBinaryA);
}
void V_b(void){
  xSemaphoreGive(SemBinaryB);
}
void V_mutex(void){
  xSemaphoreGive(mutex);
}
