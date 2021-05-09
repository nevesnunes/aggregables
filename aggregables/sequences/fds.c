#include <stdio.h>
#include <stdlib.h>

int main() {
    FILE *f1 = fopen("/tmp/f1.txt", "a+");
    FILE *f2 = fopen("/tmp/f2.txt", "a+");
    FILE *f3 = fopen("/tmp/f3.txt", "a+");
    fclose(f2);

    getchar();
    fprintf(f1, "%s", "foo");
    char *c = malloc(2);
    fread(c, 1, 1, f3);

    return 0;
}
