#include "stdio.h"
#include "stdlib.h"
#include "unistd.h"

void output(char *msg) { printf("%s\n", msg); }

int main() {
    sleep(4);
    int k = 13;
    for (int i = 0; i < 100; i++) {
        if (k % 2 == 0) {
            output("if");
            k = k ^ 17 + 31;
        } else {
            output("else");
            for (int j = 0; j < 31; j++) {
                k++;
            }
        }
    }
    printf("%d", k);
}
