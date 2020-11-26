#include "stdio.h"
#include "stdlib.h"

int main() {
    int k = 13;
    for (int i = 0; i < 100; i++) {
        if (k % 2 == 0) {
            printf("if\n");
            k = k ^ 17 + 31;
        } else {
            printf("else\n");
            for (int j = 0; j < 31; j++) {
                k++;
            }
        }
    }
    printf("%d", k);
}
