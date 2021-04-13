#include "stdio.h"
#include "stdlib.h"
#include "unistd.h"

int unused() {
    return 1;
}

void output(char *msg) { printf("%s\n", msg); }

int main() {
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
    access("/tmp/1", F_OK);
    printf("%d", k);
}
