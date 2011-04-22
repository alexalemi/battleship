#include <stdlib.h> 
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <time.h>
#include <vector>
#include <math.h>

//Instructions
//g++ BenWrapper.cpp -o adamsucks
//'/home/ben/Desktop/adamsucks'

using namespace std;

char convert(int);
char direction(int);

int main(){

	double Gameboard[10][10];
	for (int i=0; i<10; i++){
		for (int j=0; j<10; j++){
			Gameboard[i][j]=0;
		}
	}

	int viewGameboard[10][10];
	for (int i=0; i<10; i++){
		for (int j=0; j<10; j++){
			viewGameboard[i][j]=0;
		}
	}

	int lastN = 0;
	int lastA = 0;
	int sink = 0;

	srand(time(NULL));
	bool running=true;
	while (running){
		fprintf(stdout,">");
		char buf[256];
		short junk;
		junk=fscanf(stdin, "%s", buf);

		if (buf[0] == 'N'){
			//run your new game function
			//Place the ships in a random orientation

////Clear the board

	for (int i=0; i<10; i++){
		for (int j=0; j<10; j++){
			Gameboard[i][j]=0;
		}
	}

	for (int i=0; i<10; i++){
		for (int j=0; j<10; j++){
			viewGameboard[i][j]=0;
		}
	}

	lastN = 0;
	lastA = 0;
	sink = 0;

///////////////////

			int CarrierN = rand()%10+1;
			int CarrierA = rand()%10+1;
			char CarrierAnew;
			CarrierAnew = convert(CarrierA);
			int CarrierDirection = rand()%2+1;
			char CarrierDirectionnew = direction(CarrierDirection);

			while ((CarrierDirection == 2 && CarrierN > 5) || (CarrierDirection == 1 && CarrierA > 5)){
				CarrierN = rand()%10+1;
				CarrierA = rand()%10+1;
				CarrierAnew = convert(CarrierA);
				CarrierDirection = rand()%2+1;
				CarrierDirectionnew = direction(CarrierDirection);
			}

			int board[10][10];
			for (int i=0; i<10; i++){
				for (int j=0; j<10; j++){
					board[i][j]=0;
				}
			}

			if (CarrierDirection == 1){
				for (int i=1; i<=5; i++){
					board[CarrierN-1][CarrierA-1+i]=1;
				}
			}

			if (CarrierDirection == 2){
				for (int i=1; i<=5; i++){
					board[CarrierN-1+i][CarrierA-1]=1;
				}
			}
				
////Place the Battleship
		
			int BattleN = rand()%10+1;
			int BattleA = rand()%10+1;
			char BattleAnew;
			BattleAnew = convert(BattleA);
			int BattleDirection = rand()%2+1;
			char BattleDirectionnew = direction(BattleDirection);
			bool check = 0;


			if (BattleDirection == 1){
				for (int i=1; i<=4; i++){
					if (board[BattleN-1][BattleA-1+i]!=0){check = 1;}
				}
			}


			if (BattleDirection == 2){
				for (int i=1; i<=4; i++){
					if (board[BattleN-1+i][BattleA-1]!=0){check = 1;}
				}
			}
						

			while ((BattleDirection == 2 && BattleN > 6) || (BattleDirection == 1 && BattleA > 6) || check){
				check = 0;
				BattleN = rand()%10+1;
				BattleA = rand()%10+1;
				BattleAnew = convert(BattleA);
				BattleDirection = rand()%2+1;
				BattleDirectionnew = direction(BattleDirection);
				if (BattleDirection == 1){
					for (int i=1; i<=4; i++){
						if (board[BattleN-1][BattleA-1+i]!=0){check = 1;}
					}
				}

				if (BattleDirection == 2){
					for (int i=1; i<=4; i++){
						if (board[BattleN-1+i][BattleA-1]!=0){check = 1;}
					}
				}
			}

			if (BattleDirection == 1){
				for (int i=1; i<=4; i++){
					board[BattleN-1][BattleA-1+i]=2;
				}
			}

			if (BattleDirection == 2){
				for (int i=1; i<=4; i++){
					board[BattleN-1+i][BattleA-1]=2;
				}
			}

////Place the Destroyer

			int DesN = rand()%10+1;
			int DesA = rand()%10+1;
			char DesAnew;
			DesAnew = convert(DesA);
			int DesDirection = rand()%2+1;
			char DesDirectionnew = direction(DesDirection);
			check = 0;


			if (DesDirection == 1){
				for (int i=0; i<=2; i++){
					if (board[DesN-1][DesA-1+i]!=0){check = 1;}
				}
			}


			if (DesDirection == 2){
				for (int i=0; i<=2; i++){
					if (board[DesN-1+i][DesA-1]!=0){check = 1;}
				}
			}
						

			while ((DesDirection == 2 && DesN > 7) || (DesDirection == 1 && DesA > 7) || check){
				check = 0;
				DesN = rand()%10+1;
				DesA = rand()%10+1;
				DesAnew = convert(DesA);
				DesDirection = rand()%2+1;
				DesDirectionnew = direction(DesDirection);
				if (DesDirection == 1){
					for (int i=0; i<=2; i++){
						if (board[DesN-1][DesA-1+i]!=0){check = 1;}
					}
				}

				if (DesDirection == 2){
					for (int i=0; i<=2; i++){
						if (board[DesN-1+i][DesA-1]!=0){check = 1;}
					}
				}
			}

			if (DesDirection == 1){
				for (int i=0; i<=2; i++){
					board[DesN-1][DesA-1+i]=3;
				}
			}

			if (DesDirection == 2){
				for (int i=0; i<=2; i++){
					board[DesN-1+i][DesA-1]=3;
				}
			}

////Place the Submarine

			int SubN = rand()%10+1;
			int SubA = rand()%10+1;
			char SubAnew;
			SubAnew = convert(SubA);
			int SubDirection = rand()%2+1;
			char SubDirectionnew = direction(SubDirection);
			check = 0;


			if (SubDirection == 1){
				for (int i=0; i<=2; i++){
					if (board[SubN-1][SubA-1+i]!=0){check = 1;}
				}
			}


			if (SubDirection == 2){
				for (int i=0; i<=2; i++){
					if (board[SubN-1+i][SubA-1]!=0){check = 1;}
				}
			}
						

			while ((SubDirection == 2 && SubN > 7) || (SubDirection == 1 && SubA > 7) || check){
				check = 0;
				SubN = rand()%10+1;
				SubA = rand()%10+1;
				SubAnew = convert(SubA);
				SubDirection = rand()%2+1;
				SubDirectionnew = direction(SubDirection);
				if (SubDirection == 1){
					for (int i=0; i<=2; i++){
						if (board[SubN-1][SubA-1+i]!=0){check = 1;}
					}
				}

				if (SubDirection == 2){
					for (int i=0; i<=2; i++){
						if (board[SubN-1+i][SubA-1]!=0){check = 1;}
					}
				}
			}

			if (SubDirection == 1){
				for (int i=0; i<=2; i++){
					board[SubN-1][SubA-1+i]=4;
				}
			}

			if (SubDirection == 2){
				for (int i=0; i<=2; i++){
					board[SubN-1+i][SubA-1]=4;
				}
			}

////Place the Patrol Boat

			int PatrolN = rand()%10+1;
			int PatrolA = rand()%10+1;
			char PatrolAnew;
			PatrolAnew = convert(PatrolA);
			int PatrolDirection = rand()%2+1;
			char PatrolDirectionnew = direction(PatrolDirection);
			check = 0;


			if (PatrolDirection == 1){
				for (int i=0; i<=1; i++){
					if (board[PatrolN-1][PatrolA-1+i]!=0){check = 1;}
				}
			}


			if (PatrolDirection == 2){
				for (int i=0; i<=1; i++){
					if (board[PatrolN-1+i][PatrolA-1]!=0){check = 1;}
				}
			}
						

			while ((PatrolDirection == 2 && PatrolN > 8) || (PatrolDirection == 1 && PatrolA > 8) || check){
				check = 0;
				PatrolN = rand()%10+1;
				PatrolA = rand()%10+1;
				PatrolAnew = convert(PatrolA);
				PatrolDirection = rand()%2+1;
				PatrolDirectionnew = direction(PatrolDirection);
				if (PatrolDirection == 1){
					for (int i=0; i<=1; i++){
						if (board[PatrolN-1][PatrolA-1+i]!=0){check = 1;}
					}
				}

				if (PatrolDirection == 2){
					for (int i=0; i<=1; i++){
						if (board[PatrolN-1+i][PatrolA-1]!=0){check = 1;}
					}
				}
			}

			if (PatrolDirection == 1){
				for (int i=0; i<=1; i++){
					board[PatrolN-1][PatrolA-1+i]=5;
				}
			}

			if (PatrolDirection == 2){
				for (int i=0; i<=1; i++){
					board[PatrolN-1+i][PatrolA-1]=5;
				}
			}

///////Output

			fprintf(stdout, "%c%i%c %c%i%c %c%i%c %c%i%c %c%i%c", CarrierAnew, CarrierN%10, CarrierDirectionnew, BattleAnew, BattleN%10, BattleDirectionnew, DesAnew, DesN%10, DesDirectionnew, SubAnew, SubN%10, SubDirectionnew, PatrolAnew, PatrolN%10, PatrolDirectionnew);


			//Display the Grid
			/*
			cout << endl;

			for (int i=0; i<=9; i++){
				for (int j=0; j<=9; j++){
					cout << board[i][j] << " ";
				}
				cout << endl;
			}
			*/

			//fprintf(stdout, "A1R A2R A3R A4R A5R");
		}else if (buf[0] == 'F'){
			//run your firing function

			//Find the Maximum
			double max = -99999;
			vector<int> maxi;
			vector<int> maxj;
			int maxlength=0;

			for (int i=0; i<10; i++){
				for (int j=0; j<10; j++){
					if (Gameboard[i][j]>=max){max = Gameboard[i][j];} 
				}
			}

			//cout << max << endl;

			for (int i=0; i<10; i++){
				for (int j=0; j<10; j++){
					if (Gameboard[i][j]==max){maxi.push_back(i);maxj.push_back(j);maxlength++;} 
				}
			}

			int Guess = rand()%maxlength;	
			lastN = maxi[Guess];
			lastA = maxj[Guess];

			viewGameboard[lastN][lastA]=1;

/*
			for (int i=0; i<=9; i++){
				for (int j=0; j<=9; j++){
					cout << viewGameboard[i][j] << " ";
				}
				cout << endl;
			}

			cout << endl;

			for (int i=0; i<=9; i++){
				for (int j=0; j<=9; j++){
					cout << Gameboard[i][j] << " ";
				}
				cout << endl;
			}
*/

			char hold;
			hold = convert(lastA+1);
			fprintf(stdout, "%c%i", hold, lastN%10);

		}else if (buf[0] == 'H'){
			//run your "I got a hit" funtion

			viewGameboard[lastN][lastA]=2;

			for (int i=lastN; i<10; i++){
				for(int j=lastA; j<10; j++){
					Gameboard[i][j] = Gameboard[i][j] + exp(-abs(double(i)-double(lastN))-abs(double(j)-double(lastA)));
					}
			}

			for (int i=lastN; i>-1; i--){
				for(int j=lastA; j<10; j++){
					Gameboard[i][j] = Gameboard[i][j] + exp(-abs(double(i)-double(lastN))-abs(double(j)-double(lastA)));
					}
			}

			for (int i=lastN; i<10; i++){
				for(int j=lastA; j>-1; j--){
					Gameboard[i][j] = Gameboard[i][j] + exp(-abs(double(i)-double(lastN))-abs(double(j)-double(lastA)));
					}
			}

			for (int i=lastN; i>-1; i--){
				for(int j=lastA; j>-1; j--){
					Gameboard[i][j] = Gameboard[i][j] + exp(-abs(double(i)-double(lastN))-abs(double(j)-double(lastA)));
					}
			}	

			Gameboard[lastN][lastA] = -9999999;

			//Gameboard[lastN][lastA]++;//Add one to all the squares surrounding it as well?
		}else if (buf[0] == 'M'){
			//run your "I missed" function

			viewGameboard[lastN][lastA]=8;

			for (int i=lastN; i<10; i++){
				for(int j=lastA; j<10; j++){
					Gameboard[i][j] = Gameboard[i][j] - exp(-abs(double(i)-double(lastN))-abs(double(j)-double(lastA)));
					}
			}


			for (int i=lastN-1; i>-1; i--){
				for(int j=lastA; j<10; j++){
					Gameboard[i][j] = Gameboard[i][j] - exp(-abs(double(i)-double(lastN))-abs(double(j)-double(lastA)));
					}
			}

			for (int i=lastN; i<10; i++){
				for(int j=lastA-1; j>-1; j--){
					Gameboard[i][j] = Gameboard[i][j] - exp(-abs(double(i)-double(lastN))-abs(double(j)-double(lastA)));
					}
			}

			for (int i=lastN-1; i>-1; i--){
				for(int j=lastA-1; j>-1; j--){
					Gameboard[i][j] = Gameboard[i][j] - exp(-abs(double(i)-double(lastN))-abs(double(j)-double(lastA)));
					}
			}	

			Gameboard[lastN][lastA] = -9999999;
		}else if (buf[0] == 'S'){
			//run your "I sunk a ship" function (put a pentalty on the ones around, just as before)
			
			viewGameboard[lastN][lastA]=3;

			for (int i=lastN; i<10; i++){
				for(int j=lastA; j<10; j++){
					Gameboard[i][j] = Gameboard[i][j] - exp(-abs(double(i)-double(lastN))-abs(double(j)-double(lastA)));
					}
			}


			for (int i=lastN-1; i>-1; i--){
				for(int j=lastA; j<10; j++){
					Gameboard[i][j] = Gameboard[i][j] - exp(-abs(double(i)-double(lastN))-abs(double(j)-double(lastA)));
					}
			}

			for (int i=lastN; i<10; i++){
				for(int j=lastA-1; j>-1; j--){
					Gameboard[i][j] = Gameboard[i][j] - exp(-abs(double(i)-double(lastN))-abs(double(j)-double(lastA)));
					}
			}

			for (int i=lastN-1; i>-1; i--){
				for(int j=lastA-1; j>-1; j--){
					Gameboard[i][j] = Gameboard[i][j] - exp(-abs(double(i)-double(lastN))-abs(double(j)-double(lastA)));
					}
			}	

			Gameboard[lastN][lastA] = -9999999;

		}else if (buf[0] == 'O'){
			//run your "my opponent made a guess" function
		}else if (buf[0] == 'W'){
			//run your "I won" routine
		}else if (buf[0] == 'L'){
			//run your "I lost" routine
		}else if (buf[0] == 'K'){
			running=false;
		}else if (buf[0] == 'E'){
			//run your "I made an error" function
		}else{
			fprintf(stdout, "\n");
			fflush(stdout);
		}
	}

	return 0;
}

char convert(int num){

	char letter;
	if (num == 1){letter = 'A';}
	else if (num == 2){letter = 'B';}
	else if (num == 3){letter = 'C';}
	else if (num == 4){letter = 'D';}
	else if (num == 5){letter = 'E';}
	else if (num == 6){letter = 'F';}
	else if (num == 7){letter = 'G';}
	else if (num == 8){letter = 'H';}
	else if (num == 9){letter = 'I';}
	else if (num == 10){letter = 'J';}

return letter;

}

char direction(int num){

	char letter;
	if (num == 1){letter = 'R';}
	else if (num == 2){letter = 'D';}

return letter;

}
