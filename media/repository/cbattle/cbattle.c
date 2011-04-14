#include <stdlib.h>
#include <stdio.h>

void printMove();
void createBoard();

int main(){
  int fightingthefaces = 1;

  while (fightingthefaces){
    // read some stdin
    fprintf(stdout,">");
    char buf[256];
    fscanf(stdin, "%s", buf);

    if (buf[0] == 'N')
      createBoard();

    else if (buf[0] == 'F')
      printMove();

    else if (buf[0] == 'K')
      fightingthefaces = 0;
 
    else {
      fprintf(stdout, "\n");
     fflush(stdout);
    }
  }

  return 0;
}


void printMove(){
  fprintf(stdout, "%c%i\n", (char)(rand()%10 + 65), rand()%10);
  fflush(stdout);
}


void createBoard(){
  fprintf(stdout, "A0D B0D C0D D0D E0D\n");
  fflush(stdout);
}
