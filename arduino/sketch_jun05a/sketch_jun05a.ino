#include <WiFi.h>
#include <WebServer.h>
#include <ESP32_CAM.h>

// Configura tu red WiFi
const char* ssid = "tu_ssid";
const char* password = "tu_password";

// Inicializa el servidor web
WebServer server(80);

// Configura el pin de control IO0 del ESP32-CAM
const int pinIO0 = 14;

void setup() {
  // Inicializa la comunicación serial
  Serial.begin(115200);

  // Configura el pin IO0
  pinMode(pinIO0, OUTPUT);
  digitalWrite(pinIO0, HIGH);  // Modo ejecución

  // Conéctate a la red WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Conectado a la red WiFi");

  // Inicializa la cámara
  if (!initCamera()) {
    Serial.println("Error inicializando la cámara");
    return;
  }

  // Configura el servidor web
  server.on("/", handleRoot);
  server.begin();
  Serial.println("Servidor iniciado");
}

void loop() {
  server.handleClient();
}

// Función para inicializar la cámara
bool initCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = 5;
  config.pin_d1 = 18;
  config.pin_d2 = 19;
  config.pin_d3 = 21;
  config.pin_d4 = 36;
  config.pin_d5 = 39;
  config.pin_d6 = 34;
  config.pin_d7 = 35;
  config.pin_xclk = 0;
  config.pin_pclk = 22;
  config.pin_vsync = 25;
  config.pin_href = 23;
  config.pin_sccb_sda = 26;
  config.pin_sccb_scl = 27;
  config.pin_pwdn = 32;
  config.pin_reset = -1;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  if (psramFound()) {
    config.frame_size = FRAMESIZE_UXGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  // Inicializa la cámara con la configuración anterior
  if (esp_camera_init(&config) != ESP_OK) {
    return false;
  }

  return true;
}

// Función para manejar la solicitud raíz
void handleRoot() {
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    server.send(500, "text/plain", "Error capturando imagen");
    return;
  }

  server.send(200, "image/jpeg", (const char *)fb->buf, fb->len);
  esp_camera_fb_return(fb);
}
