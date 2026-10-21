if(COMMAND idf_component_register)
  idf_component_register(
    SRCS "src/dial_clock.c" "src/dial_input.c" "src/dial_motor_timing.c"
         "src/dial_rtc_ds3231.c"
    INCLUDE_DIRS "include"
  )
  return()
endif()

cmake_minimum_required(VERSION 3.16)
project(dialcanvas_clock_core C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

add_library(dial_clock_core src/dial_clock.c src/dial_input.c src/dial_motor_timing.c
                            src/dial_rtc_ds3231.c)
target_include_directories(dial_clock_core PUBLIC include)
target_compile_options(dial_clock_core PRIVATE -Wall -Wextra -Werror -pedantic)

include(CTest)
if(BUILD_TESTING)
  add_executable(test_dial_clock tests/test_dial_clock.c)
  target_link_libraries(test_dial_clock PRIVATE dial_clock_core m)
  target_compile_options(test_dial_clock PRIVATE -Wall -Wextra -Werror -pedantic)
  add_test(NAME dial_clock_math COMMAND test_dial_clock)
  add_executable(test_dial_input tests/test_dial_input.c)
  target_link_libraries(test_dial_input PRIVATE dial_clock_core)
  target_compile_options(test_dial_input PRIVATE -Wall -Wextra -Werror -pedantic)
  add_test(NAME dial_encoder_and_selection COMMAND test_dial_input)
  add_executable(test_dial_motor_timing tests/test_dial_motor_timing.c)
  target_link_libraries(test_dial_motor_timing PRIVATE dial_clock_core)
  target_compile_options(test_dial_motor_timing PRIVATE -Wall -Wextra -Werror -pedantic)
  add_test(NAME dial_motor_step_timing COMMAND test_dial_motor_timing)
  add_executable(test_dial_rtc_ds3231 tests/test_dial_rtc_ds3231.c)
  target_link_libraries(test_dial_rtc_ds3231 PRIVATE dial_clock_core)
  target_compile_options(test_dial_rtc_ds3231 PRIVATE -Wall -Wextra -Werror -pedantic)
  add_test(NAME dial_rtc_ds3231_conversion COMMAND test_dial_rtc_ds3231)
endif()
