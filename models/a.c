#include <stdio.h>

float foo(int a) {
    float b = 1.0;
    for (int i = 0; i < a; i++) {
        b = a * a;
    }
    return b;
}