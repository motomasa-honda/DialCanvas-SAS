#ifndef DIAL_INPUT_H
#define DIAL_INPUT_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/*
 * Decode one quadrature transition. State bit 1 is encoder A, bit 0 is B.
 * The sequence 00 -> 01 -> 11 -> 10 -> 00 returns +1 per edge.
 * Invalid two-bit jumps and unchanged samples return 0.
 */
int8_t dial_encoder_transition(uint8_t previous_state, uint8_t current_state);

/* Move an index by one item with wraparound. Invalid arguments return index. */
uint16_t dial_index_step(uint16_t index, uint16_t item_count, int8_t direction);

/* Allow only 1..32 ASCII letters, digits, underscore, or hyphen. */
bool dial_name_is_safe(const char *name);

/*
 * Return where candidate belongs in a sorted catalog limited to capacity.
 * SIZE_MAX means duplicate, unsafe, invalid arguments, or outside the first
 * capacity names. Existing names must be sorted and item_count <= capacity.
 */
size_t dial_catalog_insertion_index(const char *const sorted_names[],
                                    size_t item_count, size_t capacity,
                                    const char *candidate);

#endif
