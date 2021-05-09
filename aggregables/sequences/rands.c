#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void a() { printf("a\n"); }

void b() { printf("b\n"); }

int main(void) {
    srand(time(0));
    for (int i = 0; i < 10; i++) {
        switch (rand() % 5) {
        case 1:
            printf("1\n");
        case 2:
            a();
            break;
        case 3:
            b();
            break;
        default:
            printf("default\n");
        }
    }

    return 0;
}
