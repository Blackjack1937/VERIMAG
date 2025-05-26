/* toy vuln that crashes when x == 0xDEADBEEF */
   
#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    unsigned int x;
    if (scanf("%u", &x) != 1) return 0;

    if (x == 0xDEADBEEF) {  //magic
        char *p = NULL;  //deliberate segfault
        *p = 'X';
    }
    printf("OK (x=%u)\n", x);
    return 0;
}
