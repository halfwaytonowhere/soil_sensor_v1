// /*   Unless required by applicable law or agreed to in writing, this
//    software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
//    CONDITIONS OF ANY KIND, either express or implied.
// */
// #include <stdio.h>
// #include "driver/ledc.h"
// #include "esp_err.h"

// #define LEDC_TIMER              LEDC_TIMER_0
// #define LEDC_MODE               LEDC_LOW_SPEED_MODE
// #define LEDC_OUTPUT_IO          (5) // Define the output GPIO
// #define LEDC_CHANNEL            LEDC_CHANNEL_0
// #define LEDC_DUTY_RES           LEDC_TIMER_13_BIT // Set duty resolution to 13 bits
// #define LEDC_DUTY               (4095) // Set duty to 50%. ((2 ** 13) - 1) * 50% = 4095
// #define LEDC_FREQUENCY          (2) // Frequency in Hertz. Set frequency at 5 kHz

// static void example_ledc_init(void)
// {
//     // Prepare and then apply the LEDC PWM timer configuration
//     ledc_timer_config_t ledc_timer = {
//         .speed_mode       = LEDC_MODE,
//         .timer_num        = LEDC_TIMER,
//         .duty_resolution  = LEDC_DUTY_RES,
//         .freq_hz          = LEDC_FREQUENCY,  // Set output frequency at 5 kHz
//         .clk_cfg          = LEDC_AUTO_CLK
//     };
//     ESP_ERROR_CHECK(ledc_timer_config(&ledc_timer));

//     // Prepare and then apply the LEDC PWM channel configuration
//     ledc_channel_config_t ledc_channel = {
//         .speed_mode     = LEDC_MODE,
//         .channel        = LEDC_CHANNEL,
//         .timer_sel      = LEDC_TIMER,
//         .intr_type      = LEDC_INTR_DISABLE,
//         .gpio_num       = LEDC_OUTPUT_IO,
//         .duty           = 0, // Set duty to 0%
//         .hpoint         = 0
//     };
//     ESP_ERROR_CHECK(ledc_channel_config(&ledc_channel));
// }

// void app_main(void)
// {
//     // Set the LEDC peripheral configuration
//     example_ledc_init();
//     // Set duty to 50%
//     ESP_ERROR_CHECK(ledc_set_duty(LEDC_MODE, LEDC_CHANNEL, LEDC_DUTY));
//     // Update duty to apply the new value
//     ESP_ERROR_CHECK(ledc_update_duty(LEDC_MODE, LEDC_CHANNEL));
// }

#include <stdio.h>
#include <stdlib.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/adc.h"
#include "esp_adc_cal.h"
#include "main.h"

// uint32_t mape(uint32_t x, uint32_t in_min, uint32_t in_max, uint32_t out_min, uint32_t out_max)
// {
//     return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
// }

void app_main() {
    adc1_config_width(ADC_WIDTH_BIT_11); // konfiguracja rozdzielczości ADC na 12 bitów
    adc1_config_channel_atten( ADC1_CHANNEL_0, ADC_ATTEN_DB_11);
    // adc1_config_channel_atten(ADC1_CHANNEL_0, ADC_ATTEN_DB_11); // konfiguracja kanału ADC1 do odczytu wartości z czujnika wilgotności gleby pojemnościowego
    esp_adc_cal_characteristics_t adc_cal;
    esp_adc_cal_characterize( ADC_UNIT_1, ADC_ATTEN_DB_11, ADC_WIDTH_BIT_11, 1100, &adc_cal);   
    while(1) {
        uint32_t odczyt = 0;
        uint32_t soil_moisture=0;
        vTaskDelay(1000 / portTICK_PERIOD_MS); // opóźnienie wykonywania pętli głównej
        for (uint8_t i=0; i<4; i++)
        {
            uint16_t value = adc1_get_raw(ADC1_CHANNEL_0); // badam wartość na pinie ADC5
            // soil_moisture = mape(value, 2000, 1100, 0, 100);
            odczyt += value;    
        }
        odczyt = odczyt/4;
        uint16_t voltage = esp_adc_cal_raw_to_voltage(odczyt, &adc_cal);
        // printf("Soil moisture: %ld%%\n", soil_moisture);
        printf("odczyt: %ld\n", odczyt);
        printf("mv: %d\n", voltage);
        
    }
}



// #include <stdio.h>
// #include <stdlib.h>
// #include "freertos/FreeRTOS.h"
// #include "freertos/task.h"
// #include "driver/adc.h"
// #include "esp_adc_cal.h"

// #define DEFAULT_VREF    1100        // Standard voltage reference
// #define NO_OF_SAMPLES   64          // ADC sample count for smoothing
// #define SENSOR_PIN      ADC1_CHANNEL_0  // ADC pin used by the sensor

// static esp_adc_cal_characteristics_t *adc_chars;

// // Map a value from one range to another
// uint32_t mape(uint32_t x, uint32_t in_min, uint32_t in_max, uint32_t out_min, uint32_t out_max)
// {
//     return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
// }
// void app_main()
// {
//     adc1_config_width(ADC_WIDTH_BIT_12);                 // 12-bit ADC resolution
//     adc1_config_channel_atten(SENSOR_PIN, ADC_ATTEN_DB_11);   // Set the attenuation for the ADC channel

//     // Configure ADC calibration
//     adc_chars = calloc(1, sizeof(esp_adc_cal_characteristics_t));
//     esp_adc_cal_characterize(ADC_UNIT_1, ADC_ATTEN_DB_11, ADC_WIDTH_BIT_12, DEFAULT_VREF, adc_chars);

//     while (1) {
//         uint32_t adc_reading = 0;
//         // Perform multiple ADC readings and average the results for smoothing
//         for (int i = 0; i < NO_OF_SAMPLES; i++) {
//             adc_reading += adc1_get_raw(SENSOR_PIN);
//         }
//         adc_reading /= NO_OF_SAMPLES;
//         // Convert the ADC reading to a voltage
//         uint32_t voltage = esp_adc_cal_raw_to_voltage(adc_reading, adc_chars);
//         // Calculate the soil moisture percentage based on the voltage
//         uint32_t soil_moisture = mape(voltage, 2000, 1100, 0, 100);
//         printf("Soil moisture: %ld%%\n", soil_moisture);
//         vTaskDelay(pdMS_TO_TICKS(5000));    // Wait for 5 seconds before taking another reading
//     }
// }
 
