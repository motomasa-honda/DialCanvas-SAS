#include "dial_input.h"

#include <stddef.h>
#include <string.h>

int8_t dial_encoder_transition(uint8_t previous_state, uint8_t current_state)
{
    static const int8_t transitions[16] = {
         0,  1, -1,  0,
        -1,  0,  0,  1,
         1,  0,  0, -1,
         0, -1,  1,  0,
    };

    if (previous_state > 3U || current_state > 3U) {
        return 0;
    }
    return transitions[(previous_state << 2U) | current_state];
}

uint16_t dial_index_step(uint16_t index, uint16_t item_count, int8_t direction)
{
    if (item_count == 0U || index >= item_count || direction == 0) {
        return index;
    }
    if (direction > 0) {
        return (uint16_t)((index + 1U) % item_count);
    }
    return (index == 0U) ? (uint16_t)(item_count - 1U) : (uint16_t)(index - 1U);
}

bool dial_name_is_safe(const char *name)
{
    if (name == NULL || name[0] == '\0') {
        return false;
    }
    for (size_t i = 0; i <= 32U; ++i) {
        unsigned char ch = (unsigned char)name[i];
        if (ch == '\0') {
            return i > 0U;
        }
        if (i == 32U || !((ch >= 'A' && ch <= 'Z') ||
                          (ch >= 'a' && ch <= 'z') ||
                          (ch >= '0' && ch <= '9') ||
                          ch == '_' || ch == '-')) {
            return false;
        }
    }
    return false;
}

size_t dial_catalog_insertion_index(const char *const sorted_names[],
                                    size_t item_count, size_t capacity,
                                    const char *candidate)
{
    if (item_count > capacity || (item_count > 0U && sorted_names == NULL) ||
        !dial_name_is_safe(candidate)) {
        return SIZE_MAX;
    }

    size_t index = 0U;
    while (index < item_count &&
           strcmp(sorted_names[index], candidate) < 0) {
        ++index;
    }
    if ((index < item_count &&
         strcmp(sorted_names[index], candidate) == 0) || index >= capacity) {
        return SIZE_MAX;
    }
    return index;
}
