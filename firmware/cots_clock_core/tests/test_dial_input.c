#include "dial_input.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static void test_quadrature_sequence(void)
{
    static const uint8_t clockwise[] = {0, 1, 3, 2, 0};
    static const uint8_t counterclockwise[] = {0, 2, 3, 1, 0};

    for (uint8_t i = 0; i < 4U; ++i) {
        assert(dial_encoder_transition(clockwise[i], clockwise[i + 1U]) == 1);
        assert(dial_encoder_transition(counterclockwise[i], counterclockwise[i + 1U]) == -1);
    }
}

static void test_invalid_quadrature_samples(void)
{
    assert(dial_encoder_transition(0, 0) == 0);
    assert(dial_encoder_transition(0, 3) == 0);
    assert(dial_encoder_transition(3, 0) == 0);
    assert(dial_encoder_transition(4, 0) == 0);
}

static void test_index_wrap(void)
{
    assert(dial_index_step(0, 3, -1) == 2);
    assert(dial_index_step(2, 3, 1) == 0);
    assert(dial_index_step(1, 3, 1) == 2);
    assert(dial_index_step(1, 3, -1) == 0);
    assert(dial_index_step(0, 0, 1) == 0);
    assert(dial_index_step(3, 3, 1) == 3);
    assert(dial_index_step(1, 3, 0) == 1);
}

static void test_safe_dial_names(void)
{
    char maximum_length[34];
    memset(maximum_length, 'a', 32U);
    maximum_length[32] = '\0';
    maximum_length[33] = '\0';
    char over_length[34];
    memset(over_length, 'a', 33U);
    over_length[33] = '\0';

    assert(dial_name_is_safe("Forest-1"));
    assert(dial_name_is_safe("Night_Mode"));
    assert(dial_name_is_safe(maximum_length));
    assert(!dial_name_is_safe(NULL));
    assert(!dial_name_is_safe(""));
    assert(!dial_name_is_safe("../Forest"));
    assert(!dial_name_is_safe("Night Mode"));
    assert(!dial_name_is_safe("夜"));
    assert(!dial_name_is_safe(over_length));
}

static void test_sorted_catalog_keeps_first_capacity_names(void)
{
    static const char *const names[] = {"Aster", "Birch", "Cedar"};
    static const char *const full_names[] = {"Aster", "Birch", "Cedar", "Elm"};

    assert(dial_catalog_insertion_index(names, 3U, 4U, "Dogwood") == 3U);
    assert(dial_catalog_insertion_index(names, 3U, 4U, "Alder") == 0U);
    assert(dial_catalog_insertion_index(names, 3U, 4U, "Birch") == SIZE_MAX);
    assert(dial_catalog_insertion_index(full_names, 4U, 4U, "Dogwood") == 3U);
    assert(dial_catalog_insertion_index(full_names, 4U, 4U, "Willow") == SIZE_MAX);
    assert(dial_catalog_insertion_index(NULL, 0U, 4U, "Forest") == 0U);
    assert(dial_catalog_insertion_index(names, 4U, 3U, "Maple") == SIZE_MAX);
    assert(dial_catalog_insertion_index(names, 3U, 4U, "../Forest") == SIZE_MAX);
}

int main(void)
{
    test_quadrature_sequence();
    test_invalid_quadrature_samples();
    test_index_wrap();
    test_safe_dial_names();
    test_sorted_catalog_keeps_first_capacity_names();
    puts("PASS: encoder transitions, index wrap, safe names, and catalog order");
    return 0;
}
