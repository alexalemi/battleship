#include <stdlib.h> 
#include <stdio.h>
#include <string.h>
#include <sys/time.h>
#include <fstream>
#include <iostream>
#include <limits.h>

using namespace std;

int main(){
	for (long n=0; n<1000; n++){
		//Kill some time to make sure opponent can't get same time value for seed. Just a bit paranoid...
	}
	{
		timeval curTime;
		gettimeofday(&curTime, NULL);
		srand(7127*curTime.tv_sec+7817*curTime.tv_usec+3217);
	}
	for (long n=0; n<1000; n++){
		//And again...still paranoid.
	}

	class GameState{
		public:
			GameState(){
				opp.pat.isAlive=true;
				opp.pat.isFound=false;
				opp.pat.dir=0;
				opp.pat.row=0;
				opp.pat.col=0;
				opp.sub.isAlive=true;
				opp.sub.isFound=false;
				opp.sub.dir=0;
				opp.sub.row=0;
				opp.sub.col=0;
				opp.des.isAlive=true;
				opp.des.isFound=false;
				opp.des.dir=0;
				opp.des.row=0;
				opp.des.col=0;
				opp.bat.isAlive=true;
				opp.bat.isFound=false;
				opp.bat.dir=0;
				opp.bat.row=0;
				opp.bat.col=0;
				opp.car.isAlive=true;
				opp.car.isFound=false;
				opp.car.dir=0;
				opp.car.row=0;
				opp.car.col=0;
				strcpy(opp.name,"Unknown");
				me.pat.isAlive=true;
				me.pat.isFound=false;
				me.pat.dir=0;
				me.pat.row=0;
				me.pat.col=0;
				me.sub.isAlive=true;
				me.sub.isFound=false;
				me.sub.dir=0;
				me.sub.row=0;
				me.sub.col=0;
				me.des.isAlive=true;
				me.des.isFound=false;
				me.des.dir=0;
				me.des.row=0;
				me.des.col=0;
				me.bat.isAlive=true;
				me.bat.isFound=false;
				me.bat.dir=0;
				me.bat.row=0;
				me.bat.col=0;
				me.car.isAlive=true;
				me.car.isFound=false;
				me.car.dir=0;
				me.car.row=0;
				me.car.col=0;
				strcpy(me.name,"AdamWins.C");

				for(short row=1; row<=10; row++){
					for(short col=1; col<=10; col++){
						hitBoard[row-1][col-1]=false;
						missBoard[row-1][col-1]=false;
						sunkBoard[row-1][col-1]=false;
					}
				}
				running=true;

				guessRow=0;
				guessCol=0;
				lastGuessRow=0;
				lastGuessCol=0;

				roundMod=rand()%2;
				previousMoves=0;
			};

			void reset(){
				opp.pat.isAlive=true;
				opp.pat.isFound=false;
				opp.pat.dir=0;
				opp.pat.row=0;
				opp.pat.col=0;
				opp.sub.isAlive=true;
				opp.sub.isFound=false;
				opp.sub.dir=0;
				opp.sub.row=0;
				opp.sub.col=0;
				opp.des.isAlive=true;
				opp.des.isFound=false;
				opp.des.dir=0;
				opp.des.row=0;
				opp.des.col=0;
				opp.bat.isAlive=true;
				opp.bat.isFound=false;
				opp.bat.dir=0;
				opp.bat.row=0;
				opp.bat.col=0;
				opp.car.isAlive=true;
				opp.car.isFound=false;
				opp.car.dir=0;
				opp.car.row=0;
				opp.car.col=0;
				strcpy(opp.name,"Unknown");
				me.pat.isAlive=true;
				me.pat.isFound=false;
				me.pat.dir=0;
				me.pat.row=0;
				me.pat.col=0;
				me.sub.isAlive=true;
				me.sub.isFound=false;
				me.sub.dir=0;
				me.sub.row=0;
				me.sub.col=0;
				me.des.isAlive=true;
				me.des.isFound=false;
				me.des.dir=0;
				me.des.row=0;
				me.des.col=0;
				me.bat.isAlive=true;
				me.bat.isFound=false;
				me.bat.dir=0;
				me.bat.row=0;
				me.bat.col=0;
				me.car.isAlive=true;
				me.car.isFound=false;
				me.car.dir=0;
				me.car.row=0;
				me.car.col=0;
				strcpy(me.name,"AdamWins.C");

				for(short row=1; row<=10; row++){
					for(short col=1; col<=10; col++){
						hitBoard[row-1][col-1]=false;
						missBoard[row-1][col-1]=false;
						sunkBoard[row-1][col-1]=false;
					}
				}
				running=true;

				guessRow=0;
				guessCol=0;
				lastGuessRow=0;
				lastGuessCol=0;

				roundMod=(roundMod==0)?1:0;
				previousMoves=0;
			};

			void run(){
				running=true;
			};

			void end(){
				running=false;
			};

			void setOpponentName(char * input){
				strcpy(opp.name,input);
			};

			void placeShips(){
				short bestCarRow=0;
				short bestCarCol=0;
				short bestCarDir=0;
				short bestBatRow=0;
				short bestBatCol=0;
				short bestBatDir=0;
				short bestDesRow=0;
				short bestDesCol=0;
				short bestDesDir=0;
				short bestSubRow=0;
				short bestSubCol=0;
				short bestSubDir=0;
				short bestPatRow=0;
				short bestPatCol=0;
				short bestPatDir=0;
				long bestScore=LONG_MAX;

				long timediff=0;

				timeval startTime;
				gettimeofday(&startTime, NULL);

				while(timediff<1000000){
					bool occupied[10][10];
					for (short row=1; row<=10; row++){
						for (short col=1; col<=10; col++){
							occupied[row-1][col-1]=false;
						}
					}
					short dir=rand()%2, testRow, testCol;
					if (dir==0){
						testRow=rand()%10+1;
						testCol=rand()%6+1;
						me.car.dir=1;
						me.car.row=testRow;
						me.car.col=testCol;
						me.car.isAlive=true;
						occupied[testRow-1][testCol-1]=true;
						occupied[testRow-1][testCol]=true;
						occupied[testRow-1][testCol+1]=true;
						occupied[testRow-1][testCol+2]=true;
						occupied[testRow-1][testCol+3]=true;
					}else{
						testRow=rand()%6+1;
						testCol=rand()%10+1;
						me.car.dir=2;
						me.car.row=testRow;
						me.car.col=testCol;
						me.car.isAlive=true;
						occupied[testRow-1][testCol-1]=true;
						occupied[testRow][testCol-1]=true;
						occupied[testRow+1][testCol-1]=true;
						occupied[testRow+2][testCol-1]=true;
						occupied[testRow+3][testCol-1]=true;
					}

					bool valid=false;
					while(!valid){
						valid=true;
						dir=rand()%2;
						if (dir==0){
							testRow=rand()%10+1;
							testCol=rand()%7+1;
							for (short row2=myMax(1,testRow-1); row2<=myMin(10,testRow+1); row2++){
								for (short col2=myMax(1,testCol-1); col2<=myMin(10,testCol+4); col2++){
									if (occupied[row2-1][col2-1]){
										valid=false;
									}
								}
							}
						}else{
							testRow=rand()%7+1;
							testCol=rand()%10+1;
							for (short row2=myMax(1,testRow-1); row2<=myMin(10,testRow+4); row2++){
								for (short col2=myMax(1,testCol-1); col2<=myMin(10,testCol+1); col2++){
									if (occupied[row2-1][col2-1]){
										valid=false;
									}
								}
							}
						}
					}
					if(dir==0){
						me.bat.dir=1;
						occupied[testRow-1][testCol-1]=true;
						occupied[testRow-1][testCol]=true;
						occupied[testRow-1][testCol+1]=true;
						occupied[testRow-1][testCol+2]=true;
					}else{
						me.bat.dir=2;
						occupied[testRow-1][testCol-1]=true;
						occupied[testRow][testCol-1]=true;
						occupied[testRow+1][testCol-1]=true;
						occupied[testRow+2][testCol-1]=true;
					}
					me.bat.row=testRow;
					me.bat.col=testCol;
					me.bat.isAlive=true;

					valid=false;
					while(!valid){
						valid=true;
						dir=rand()%2;
						if (dir==0){
							testRow=rand()%10+1;
							testCol=rand()%8+1;
							for (short row2=myMax(1,testRow-1); row2<=myMin(10,testRow+1); row2++){
								for (short col2=myMax(1,testCol-1); col2<=myMin(10,testCol+3); col2++){
									if (occupied[row2-1][col2-1]){
										valid=false;
									}
								}
							}
						}else{
							testRow=rand()%8+1;
							testCol=rand()%10+1;
							for (short row2=myMax(1,testRow-1); row2<=myMin(10,testRow+3); row2++){
								for (short col2=myMax(1,testCol-1); col2<=myMin(10,testCol+1); col2++){
									if (occupied[row2-1][col2-1]){
										valid=false;
									}
								}
							}
						}
					}
					if(dir==0){
						me.des.dir=1;
						occupied[testRow-1][testCol-1]=true;
						occupied[testRow-1][testCol]=true;
						occupied[testRow-1][testCol+1]=true;
					}else{
						me.des.dir=2;
						occupied[testRow-1][testCol-1]=true;
						occupied[testRow][testCol-1]=true;
						occupied[testRow+1][testCol-1]=true;
					}
					me.des.row=testRow;
					me.des.col=testCol;
					me.des.isAlive=true;

					valid=false;
					while(!valid){
						valid=true;
						dir=rand()%2;
						if (dir==0){
							testRow=rand()%10+1;
							testCol=rand()%8+1;
							for (short row2=myMax(1,testRow-1); row2<=myMin(10,testRow+1); row2++){
								for (short col2=myMax(1,testCol-1); col2<=myMin(10,testCol+3); col2++){
									if (occupied[row2-1][col2-1]){
										valid=false;
									}
								}
							}
						}else{
							testRow=rand()%8+1;
							testCol=rand()%10+1;
							for (short row2=myMax(1,testRow-1); row2<=myMin(10,testRow+3); row2++){
								for (short col2=myMax(1,testCol-1); col2<=myMin(10,testCol+1); col2++){
									if (occupied[row2-1][col2-1]){
										valid=false;
									}
								}
							}
						}
					}
					if(dir==0){
						me.sub.dir=1;
						occupied[testRow-1][testCol-1]=true;
						occupied[testRow-1][testCol]=true;
						occupied[testRow-1][testCol+1]=true;
					}else{
						me.sub.dir=2;
						occupied[testRow-1][testCol-1]=true;
						occupied[testRow][testCol-1]=true;
						occupied[testRow+1][testCol-1]=true;
					}
					me.sub.row=testRow;
					me.sub.col=testCol;
					me.sub.isAlive=true;

					valid=false;
					while(!valid){
						valid=true;
						dir=rand()%2;
						if (dir==0){
							testRow=rand()%10+1;
							testCol=rand()%9+1;
							for (short row2=myMax(1,testRow-1); row2<=myMin(10,testRow+1); row2++){
								for (short col2=myMax(1,testCol-1); col2<=myMin(10,testCol+2); col2++){
									if (occupied[row2-1][col2-1]){
										valid=false;
									}
								}
							}
						}else{
							testRow=rand()%9+1;
							testCol=rand()%10+1;
							for (short row2=myMax(1,testRow-1); row2<=myMin(10,testRow+2); row2++){
								for (short col2=myMax(1,testCol-1); col2<=myMin(10,testCol+1); col2++){
									if (occupied[row2-1][col2-1]){
										valid=false;
									}
								}
							}
						}
					}
					if(dir==0){
						me.pat.dir=1;
						occupied[testRow-1][testCol-1]=true;
						occupied[testRow-1][testCol]=true;
					}else{
						me.pat.dir=2;
						occupied[testRow-1][testCol-1]=true;
						occupied[testRow][testCol-1]=true;
					}
					me.pat.row=testRow;
					me.pat.col=testCol;
					me.pat.isAlive=true;

					long int thisScore=0;
					if (me.car.dir==1){
						thisScore+=myMax(myMax(myMax(myMax(history[me.car.row-1][me.car.col-1],history[me.car.row][me.car.col-1]),history[me.car.row+1][me.car.col-1]),history[me.car.row+2][me.car.col-1]),history[me.car.row+3][me.car.col-1]);
					}else{
						thisScore+=myMax(myMax(myMax(myMax(history[me.car.row-1][me.car.col-1],history[me.car.row-1][me.car.col]),history[me.car.row-1][me.car.col+1]),history[me.car.row-1][me.car.col+2]),history[me.car.row-1][me.car.col+3]);
					}
					if (me.bat.dir==1){
						thisScore+=myMax(myMax(myMax(myMax(history[me.bat.row-1][me.bat.col-1],history[me.bat.row][me.bat.col-1]),history[me.bat.row+1][me.bat.col-1]),history[me.bat.row+2][me.bat.col-1]),history[me.bat.row+3][me.bat.col-1]);
					}else{
						thisScore+=myMax(myMax(myMax(myMax(history[me.bat.row-1][me.bat.col-1],history[me.bat.row-1][me.bat.col]),history[me.bat.row-1][me.bat.col+1]),history[me.bat.row-1][me.bat.col+2]),history[me.bat.row-1][me.bat.col+3]);
					}
					if (me.des.dir==1){
						thisScore+=myMax(myMax(myMax(myMax(history[me.des.row-1][me.des.col-1],history[me.des.row][me.des.col-1]),history[me.des.row+1][me.des.col-1]),history[me.des.row+2][me.des.col-1]),history[me.des.row+3][me.des.col-1]);
					}else{
						thisScore+=myMax(myMax(myMax(myMax(history[me.des.row-1][me.des.col-1],history[me.des.row-1][me.des.col]),history[me.des.row-1][me.des.col+1]),history[me.des.row-1][me.des.col+2]),history[me.des.row-1][me.des.col+3]);
					}
					if (me.sub.dir==1){
						thisScore+=myMax(myMax(myMax(myMax(history[me.sub.row-1][me.sub.col-1],history[me.sub.row][me.sub.col-1]),history[me.sub.row+1][me.sub.col-1]),history[me.sub.row+2][me.sub.col-1]),history[me.sub.row+3][me.sub.col-1]);
					}else{
						thisScore+=myMax(myMax(myMax(myMax(history[me.sub.row-1][me.sub.col-1],history[me.sub.row-1][me.sub.col]),history[me.sub.row-1][me.sub.col+1]),history[me.sub.row-1][me.sub.col+2]),history[me.sub.row-1][me.sub.col+3]);
					}
					if (me.pat.dir==1){
						thisScore+=myMax(myMax(myMax(myMax(history[me.pat.row-1][me.pat.col-1],history[me.pat.row][me.pat.col-1]),history[me.pat.row+1][me.pat.col-1]),history[me.pat.row+2][me.pat.col-1]),history[me.pat.row+3][me.pat.col-1]);
					}else{
						thisScore+=myMax(myMax(myMax(myMax(history[me.pat.row-1][me.pat.col-1],history[me.pat.row-1][me.pat.col]),history[me.pat.row-1][me.pat.col+1]),history[me.pat.row-1][me.pat.col+2]),history[me.pat.row-1][me.pat.col+3]);
					}

					if (thisScore<bestScore){
						bestScore=thisScore;
						bestCarRow=me.car.row;
						bestCarCol=me.car.col;
						bestCarDir=me.car.dir;
						bestBatRow=me.bat.row;
						bestBatCol=me.bat.col;
						bestBatDir=me.bat.dir;
						bestDesRow=me.des.row;
						bestDesCol=me.des.col;
						bestDesDir=me.des.dir;
						bestSubRow=me.sub.row;
						bestSubCol=me.sub.col;
						bestSubDir=me.sub.dir;
						bestPatRow=me.pat.row;
						bestPatCol=me.pat.col;
						bestPatDir=me.pat.dir;
					}

					timeval curTime;
					gettimeofday(&curTime, NULL);
					timediff=(curTime.tv_sec-startTime.tv_sec)*1000000+(curTime.tv_usec-startTime.tv_usec);
				}
				me.car.row=bestCarRow;
				me.car.col=bestCarCol;
				me.car.dir=bestCarDir;
				me.bat.row=bestBatRow;
				me.bat.col=bestBatCol;
				me.bat.dir=bestBatDir;
				me.des.row=bestDesRow;
				me.des.col=bestDesCol;
				me.des.dir=bestDesDir;
				me.sub.row=bestSubRow;
				me.sub.col=bestSubCol;
				me.sub.dir=bestSubDir;
				me.pat.row=bestPatRow;
				me.pat.col=bestPatCol;
				me.pat.dir=bestPatDir;
			};

			void printShips(){
				char carO, batO, desO, subO, patO;
				if(me.car.dir==1){
					carO='R';
				}else{
					carO='D';
				}
				if(me.bat.dir==1){
					batO='R';
				}else{
					batO='D';
				}
				if(me.des.dir==1){
					desO='R';
				}else{
					desO='D';
				}
				if(me.sub.dir==1){
					subO='R';
				}else{
					subO='D';
				}
				if(me.pat.dir==1){
					patO='R';
				}else{
					patO='D';
				}
				fprintf(stdout, "%c%i%c %c%i%c %c%i%c %c%i%c %c%i%c\n", (char)(me.car.col+64), me.car.row-1, carO, (char)(me.bat.col+64), me.bat.row-1, batO, (char)(me.des.col+64), me.des.row-1, desO, (char)(me.sub.col+64), me.sub.row-1, subO, (char)(me.pat.col+64), me.pat.row-1, patO);
				fflush(stdout);
			};

			void printWin(){
				//fprintf(stdout, "%s\n", "VICTORY!");
				fflush(stdout);
			};

			void printLoss(){
				//fprintf(stdout, "%s\n", "Cheater...");
				fflush(stdout);
			};

			void printError(){
				//fprintf(stdout, "%s\n", "No, YOU made an error.");
				fflush(stdout);
			};

			void printMove(){
				fprintf(stdout, "%c%i\n", (char)(guessCol+64), guessRow-1);
				fflush(stdout);
			};

			void recordHit(){
				hitBoard[guessRow-1][guessCol-1]=true;
			};

			void recordMiss(){
				missBoard[guessRow-1][guessCol-1]=true;
			};

			void sink(char * shipChar){
				if (shipChar[0] == 'C'){
					opp.car.isAlive=false;
					opp.car.row=guessRow;
					opp.car.col=guessCol;
					sunkBoard[guessRow-1][guessCol-1]=true;
				}else if (shipChar[0] == 'B'){
					opp.bat.isAlive=false;
					opp.bat.row=guessRow;
					opp.bat.col=guessCol;
					sunkBoard[guessRow-1][guessCol-1]=true;
				}else if (shipChar[0] == 'D'){
					opp.des.isAlive=false;
					opp.des.row=guessRow;
					opp.des.col=guessCol;
					sunkBoard[guessRow-1][guessCol-1]=true;
				}else if (shipChar[0] == 'S'){
					opp.sub.isAlive=false;
					opp.sub.row=guessRow;
					opp.sub.col=guessCol;
					sunkBoard[guessRow-1][guessCol-1]=true;
				}else if (shipChar[0] == 'P'){
					opp.pat.isAlive=false;
					opp.pat.row=guessRow;
					opp.pat.col=guessCol;
					sunkBoard[guessRow-1][guessCol-1]=true;
				}else{
					fprintf(stdout, "Invalid ship identifier. Cannot sink ship");
				}
			};

			bool isRunning(){
				return running;
			};

			void recordOppGuess(char * oppGuess){
				short col=(short)(oppGuess[0])-65;
				short row=(short)(oppGuess[1])-48;

				history[row][col]+=(99-previousMoves)*(99-previousMoves);
				previousMoves++;
			};

			void fakeBoard(){
				for (short row=1; row<=10; row++){
					for (short col=1; col<=10; col++){
						hitBoard[row-1][col-1]=false;
						missBoard[row-1][col-1]=false;
						sunkBoard[row-1][col-1]=false;
					}
				}
				hitBoard[4][4]=true;
				missBoard[4][3]=true;
				missBoard[4][5]=true;
				missBoard[3][4]=true;
				roundMod=0;
			};

			void pickMove(){
				for (short n=0; n<5; n++){
					locateShips();
				}
				//printBoard();

				long double score[10][10];

				for (short row=1; row<=10; row++){
					for (short col=1; col<=10; col++){
						score[row-1][col-1]=((long double)(rand()))/(100000.0*((long double)(RAND_MAX)));

						short downDist=scan(1,0,row,col);
						short upDist=scan(-1,0,row,col);
						short rightDist=scan(0,1,row,col);
						short leftDist=scan(0,-1,row,col);

						short hitScore=0;

						for (short testRow=1; testRow<=10; testRow++){
							for (short testCol=1; testCol<=10; testCol++){
								if (hitBoard[testRow-1][testCol-1] && (testRow!=row || testCol!=col) && (testCol==col || testRow==row)){
									if (testCol==col){
										if (testRow<row){
											if (opp.car.isAlive){
												for (short start=row-4; start<=testRow; start++){
												bool good=true;
													for (short cell=1; cell<=5; cell++){
														if (start+cell>11 || start+cell<2 || missBoard[start+cell-2][col-1] || sunkBoard[start+cell-2][col-1]){
															good=false;
														}
													}
													if (good){
														hitScore++;
													}
												}
											}
											if (opp.bat.isAlive){
												for (short start=myMax(1,row-3); start<=testRow; start++){
													bool good=true;
													for (short cell=1; cell<=4; cell++){
														if (start+cell>11 || missBoard[start+cell-2][col-1] || sunkBoard[start+cell-2][col-1]){
															good=false;
														}
													}
													if (good){
														hitScore++;
													}
												}
											}
											if (opp.des.isAlive){
												for (short start=myMax(1,row-2); start<=testRow; start++){
													bool good=true;
													for (short cell=1; cell<=3; cell++){
														if (start+cell>11 || missBoard[start+cell-2][col-1] || sunkBoard[start+cell-2][col-1]){
															good=false;
														}
													}
													if (good){
														hitScore++;
													}
												}
											}
											if (opp.sub.isAlive){
												for (short start=myMax(1,row-2); start<=testRow; start++){
													bool good=true;
													for (short cell=1; cell<=3; cell++){
														if (start+cell>11 || missBoard[start+cell-2][col-1] || sunkBoard[start+cell-2][col-1]){
															good=false;
														}
													}
													if (good){
														hitScore++;
													}
												}
											}
											if (opp.pat.isAlive){
												for (short start=myMax(1,row-1); start<=testRow; start++){
													bool good=true;
													for (short cell=1; cell<=2; cell++){
														if (start+cell>11 || missBoard[start+cell-2][col-1] || sunkBoard[start+cell-2][col-1]){
															good=false;
														}
													}
													if (good){
														hitScore++;
													}
												}
											}
										}else if (testRow>row){
											if (opp.car.isAlive){
												for (short start=myMax(1,testRow-4); start<=row; start++){
													bool good=true;
													for (short cell=1; cell<=5; cell++){
														if (start+cell>11 || missBoard[start+cell-2][col-1] || sunkBoard[start+cell-2][col-1]){
															good=false;
														}
													}
													if (good){
														hitScore++;
													}
												}
											}
											if (opp.bat.isAlive){
												for (short start=myMax(1,testRow-3); start<=row; start++){
													bool good=true;
													for (short cell=1; cell<=4; cell++){
														if (start+cell>11 || missBoard[start+cell-2][col-1] || sunkBoard[start+cell-2][col-1]){
															good=false;
														}
													}
													if (good){
														hitScore++;
													}
												}
											}
											if (opp.des.isAlive){
												for (short start=myMax(1,testRow-2); start<=row; start++){
													bool good=true;
													for (short cell=1; cell<=3; cell++){
														if (start+cell>11 || missBoard[start+cell-2][col-1] || sunkBoard[start+cell-2][col-1]){
															good=false;
														}
													}
													if (good){
														hitScore++;
													}
												}
											}
											if (opp.sub.isAlive){
												for (short start=myMax(1,testRow-2); start<=row; start++){
													bool good=true;
													for (short cell=1; cell<=3; cell++){
														if (start+cell>11 || missBoard[start+cell-2][col-1] || sunkBoard[start+cell-2][col-1]){
															good=false;
														}
													}
													if (good){
														hitScore++;
													}
												}
											}
											if (opp.pat.isAlive){
												for (short start=myMax(1,testRow-1); start<=row; start++){
													bool good=true;
													for (short cell=1; cell<=2; cell++){
														if (start+cell>11 || missBoard[start+cell-2][col-1] || sunkBoard[start+cell-2][col-1]){
															good=false;
														}
													}
													if (good){
														hitScore++;
													}
												}
											}
										}
									}else if (testRow==row){
										if (testCol<col){
											if (opp.car.isAlive){
												for (short start=myMax(1,col-4); start<=testCol; start++){
													bool good=true;
													for (short cell=1; cell<=5; cell++){
														if (start+cell>11 || missBoard[row-1][start+cell-2] || sunkBoard[row-1][start+cell-2]){
															good=false;
														}
													}
													if (good){
														hitScore++;
													}
												}
											}
											if (opp.bat.isAlive){
												for (short start=myMax(1,col-3); start<=testCol; start++){
													bool good=true;
													for (short cell=1; cell<=4; cell++){
														if (start+cell>11 || missBoard[row-1][start+cell-2] || sunkBoard[row-1][start+cell-2]){
															good=false;
														}
													}
													if (good){
														hitScore++;
													}
												}
											}
											if (opp.des.isAlive){
												for (short start=myMax(1,col-2); start<=testCol; start++){
													bool good=true;
													for (short cell=1; cell<=3; cell++){
														if (start+cell>11 || missBoard[row-1][start+cell-2] || sunkBoard[row-1][start+cell-2]){
															good=false;
														}
													}
													if (good){
														hitScore++;
													}
												}
											}
											if (opp.sub.isAlive){
												for (short start=myMax(1,col-2); start<=testCol; start++){
													bool good=true;
													for (short cell=1; cell<=3; cell++){
														if (start+cell>11 || missBoard[row-1][start+cell-2] || sunkBoard[row-1][start+cell-2]){
															good=false;
														}
													}
													if (good){
														hitScore++;
													}
												}
											}
											if (opp.pat.isAlive){
												for (short start=myMax(1,col-1); start<=testCol; start++){
													bool good=true;
													for (short cell=1; cell<=2; cell++){
														if (start+cell>11 || missBoard[row-1][start+cell-2] || sunkBoard[row-1][start+cell-2]){
															good=false;
														}
													}
													if (good){
														hitScore++;
													}
												}
											}
										}else if (testCol>col){
											if (opp.car.isAlive){
												for (short start=myMax(1,testCol-4); start<=col; start++){
													bool good=true;
													for (short cell=1; cell<=5; cell++){
														if (start+cell>11 || missBoard[row-1][start+cell-2] || sunkBoard[row-1][start+cell-2]){
															good=false;
														}
													}
													if (good){
														hitScore++;
													}
												}
											}
											if (opp.bat.isAlive){
												for (short start=myMax(1,testCol-3); start<=col; start++){
													bool good=true;
													for (short cell=1; cell<=4; cell++){
														if (start+cell>11 || missBoard[row-1][start+cell-2] || sunkBoard[row-1][start+cell-2]){
															good=false;
														}
													}
													if (good){
														hitScore++;
													}
												}
											}
											if (opp.des.isAlive){
												for (short start=myMax(1,testCol-2); start<=col; start++){
													bool good=true;
													for (short cell=1; cell<=3; cell++){
														if (start+cell>11 || missBoard[row-1][start+cell-2] || sunkBoard[row-1][start+cell-2]){
															good=false;
														}
													}
													if (good){
														hitScore++;
													}
												}
											}
											if (opp.sub.isAlive){
												for (short start=myMax(1,testCol-2); start<=col; start++){
													bool good=true;
													for (short cell=1; cell<=3; cell++){
														if (start+cell>11 || missBoard[row-1][start+cell-2] || sunkBoard[row-1][start+cell-2]){
															good=false;
														}
													}
													if (good){
														hitScore++;
													}
												}
											}
											if (opp.pat.isAlive){
												for (short start=myMax(1,testCol-1); start<=col; start++){
													bool good=true;
													for (short cell=1; cell<=2; cell++){
														if (start+cell>11 || missBoard[row-1][start+cell-2] || sunkBoard[row-1][start+cell-2]){
															good=false;
														}
													}
													if (good){
														hitScore++;
													}
												}
											}
										}
									}
								}
							}
						}
						score[row-1][col-1]+=10000000.0*((long double)(hitScore));

						if (opp.pat.isAlive){
							score[row-1][col-1]+=(long double)(myMax(0,(myMin(1,downDist)+myMin(1,upDist))));
							score[row-1][col-1]+=(long double)(myMax(0,(myMin(1,leftDist)+myMin(1,rightDist))));
						}
						if (opp.sub.isAlive){
							score[row-1][col-1]+=(long double)(myMax(0,(myMin(2,downDist)+myMin(2,upDist)-1)));
							score[row-1][col-1]+=(long double)(myMax(0,(myMin(2,leftDist)+myMin(2,rightDist)-1)));
						}
						if (opp.des.isAlive){
							score[row-1][col-1]+=(long double)(myMax(0,(myMin(2,downDist)+myMin(2,upDist)-1)));
							score[row-1][col-1]+=(long double)(myMax(0,(myMin(2,leftDist)+myMin(2,rightDist)-1)));
						}
						if (opp.bat.isAlive){
							score[row-1][col-1]+=(long double)(myMax(0,(myMin(3,downDist)+myMin(3,upDist)-2)));
							score[row-1][col-1]+=(long double)(myMax(0,(myMin(3,leftDist)+myMin(3,rightDist)-2)));
						}
						if (opp.car.isAlive){
							score[row-1][col-1]+=(long double)(myMax(0,(myMin(4,downDist)+myMin(4,upDist)-3)));
							score[row-1][col-1]+=(long double)(myMax(0,(myMin(4,leftDist)+myMin(4,rightDist)-3)));
						}

						if (row>2 && (missBoard[row-3][col-1] || sunkBoard[row-3][col-1])){
							score[row-1][col-1]+=0.01;
						}
						if (row<9 && (missBoard[row+1][col-1] || sunkBoard[row+1][col-1])){
							score[row-1][col-1]+=0.01;
						}
						if (col>2 && (missBoard[row-1][col-3] || sunkBoard[row-1][col-3])){
							score[row-1][col-1]+=0.01;
						}
						if (col<9 && (missBoard[row-1][col+1] || sunkBoard[row-1][col+1])){
							score[row-1][col-1]+=0.01;
						}
						if (row!=1 && col!=1 && (missBoard[row-2][col-2] || sunkBoard[row-2][col-2])){
							score[row-1][col-1]+=0.02;
						}
						if (row!=1 && col!=10 && (missBoard[row-2][col] || sunkBoard[row-2][col])){
							score[row-1][col-1]+=0.02;
						}
						if (row!=10 && col!=1 && (missBoard[row][col-2] || sunkBoard[row][col-2])){
							score[row-1][col-1]+=0.02;
						}
						if (row!=10 && col!=10 && (missBoard[row][col] || sunkBoard[row][col])){
							score[row-1][col-1]+=0.02;
						}

						if (opp.pat.isAlive && (row+col)%2==roundMod){
							score[row-1][col-1]+=0.001;
						}
					}
				}

				long double bestScore=0.0;
				for (short row=1; row<=10; row++){
					for (short col=1; col<=10; col++){
						if (score[row-1][col-1]>bestScore && !missBoard[row-1][col-1] && !hitBoard[row-1][col-1] && !sunkBoard[row-1][col-1]){
							bestScore=score[row-1][col-1];
							guessRow=row;
							guessCol=col;
						}
					}
				}
			};

			void getHistory(char * filename){
				ifstream infile(filename);
				
				for (short row=1; row<=10; row++){
					for (short col=1; col<=10; col++){
						infile >> history[row-1][col-1];
					}
				}
				infile.close();
			};

			void setHistory(char * filename){
				ofstream outfile(filename);
				for (short row=1; row<=10; row++){
					for (short col=1; col<=10; col++){
						outfile << history[row-1][col-1] << " ";
					}
					outfile << endl;
				}
				outfile << endl;
				outfile.close();
			};

			short lastRow(){
				return guessRow;
			};

			short lastCol(){
				return guessCol;
			};

		private:
			struct Player{
				struct Ship{
					short row, col, dir;
					bool isAlive, isFound;
				};
				Ship pat, sub, des, bat, car;
				char name[256];
			};
			Player me, opp;
			bool hitBoard[10][10], missBoard[10][10], sunkBoard[10][10], running;
			short guessRow, guessCol, lastGuessRow, lastGuessCol, roundMod, previousMoves;
			char junk[256];
			long history[10][10];

			short myMin(short a, short b){
				if (a<=b){
					return a;
				}else{
					return b;
				}
			};

			short myMax(short a, short b){
				if (a>=b){
					return a;
				}else{
					return b;
				}
			};

			short scan(short vert, short hor, short row, short col){
				short checkRow=row+vert;
				short checkCol=col+hor;
				bool done=false;
				short dist=0;
				while (checkRow>=1 && checkRow<=10 && checkCol>=1 && checkCol<=10 && !done){
					if (!missBoard[checkRow-1][checkCol-1] && !sunkBoard[checkRow-1][checkCol-1]){
						dist++;
					}else{
						done=true;
					}
					checkRow+=vert;
					checkCol+=hor;
				}
				return dist;
			};

			short hitScan(short vert, short hor, short row, short col){
				short checkRow=row+vert;
				short checkCol=col+hor;
				bool done=false;
				short dist=0;
				while (checkRow>=1 && checkRow<=10 && checkCol>=1 && checkCol<=10 && !done){
					if (hitBoard[checkRow-1][checkCol-1]){
						dist++;
					}else{
						done=true;
					}
					checkRow+=vert;
					checkCol+=hor;
				}
				return dist;
			};

			void locateShips(){
				if (!opp.car.isAlive && !opp.car.isFound){
					short downDist=hitScan(1,0,opp.car.row,opp.car.col);
					short upDist=hitScan(-1,0,opp.car.row,opp.car.col);
					short rightDist=hitScan(0,1,opp.car.row,opp.car.col);
					short leftDist=hitScan(0,-1,opp.car.row,opp.car.col);

					if (downDist>=4 && upDist<4 && leftDist<4 && rightDist<4){
						opp.car.dir=2;
						hitBoard[opp.car.row][opp.car.col-1]=false;
						sunkBoard[opp.car.row][opp.car.col-1]=true;
						hitBoard[opp.car.row+1][opp.car.col-1]=false;
						sunkBoard[opp.car.row+1][opp.car.col-1]=true;
						hitBoard[opp.car.row+2][opp.car.col-1]=false;
						sunkBoard[opp.car.row+2][opp.car.col-1]=true;
						hitBoard[opp.car.row+3][opp.car.col-1]=false;
						sunkBoard[opp.car.row+3][opp.car.col-1]=true;
					}else if (downDist<4 && upDist>=4 && leftDist<4 && rightDist<4){
						opp.car.dir=4;
						hitBoard[opp.car.row-2][opp.car.col-1]=false;
						sunkBoard[opp.car.row-2][opp.car.col-1]=true;
						hitBoard[opp.car.row-3][opp.car.col-1]=false;
						sunkBoard[opp.car.row-3][opp.car.col-1]=true;
						hitBoard[opp.car.row-4][opp.car.col-1]=false;
						sunkBoard[opp.car.row-4][opp.car.col-1]=true;
						hitBoard[opp.car.row-5][opp.car.col-1]=false;
						sunkBoard[opp.car.row-5][opp.car.col-1]=true;
					}else if (downDist<4 && upDist<4 && leftDist>=4 && rightDist<4){
						opp.car.dir=3;
						hitBoard[opp.car.row-1][opp.car.col-2]=false;
						sunkBoard[opp.car.row-1][opp.car.col-2]=true;
						hitBoard[opp.car.row-1][opp.car.col-3]=false;
						sunkBoard[opp.car.row-1][opp.car.col-3]=true;
						hitBoard[opp.car.row-1][opp.car.col-4]=false;
						sunkBoard[opp.car.row-1][opp.car.col-4]=true;
						hitBoard[opp.car.row-1][opp.car.col-5]=false;
						sunkBoard[opp.car.row-1][opp.car.col-5]=true;
					}else if (downDist<4 && upDist<4 && leftDist<4 && rightDist>=4){
						opp.car.dir=1;
						hitBoard[opp.car.row-1][opp.car.col]=false;
						sunkBoard[opp.car.row-1][opp.car.col]=true;
						hitBoard[opp.car.row-1][opp.car.col+1]=false;
						sunkBoard[opp.car.row-1][opp.car.col+1]=true;
						hitBoard[opp.car.row-1][opp.car.col+2]=false;
						sunkBoard[opp.car.row-1][opp.car.col+2]=true;
						hitBoard[opp.car.row-1][opp.car.col+3]=false;
						sunkBoard[opp.car.row-1][opp.car.col+3]=true;
					}
				}
				if (!opp.bat.isAlive && !opp.bat.isFound){
					short downDist=hitScan(1,0,opp.bat.row,opp.bat.col);
					short upDist=hitScan(-1,0,opp.bat.row,opp.bat.col);
					short rightDist=hitScan(0,1,opp.bat.row,opp.bat.col);
					short leftDist=hitScan(0,-1,opp.bat.row,opp.bat.col);

					if (downDist>=3 && upDist<3 && leftDist<3 && rightDist<3){
						opp.bat.dir=2;
						hitBoard[opp.bat.row][opp.bat.col-1]=false;
						sunkBoard[opp.bat.row][opp.bat.col-1]=true;
						hitBoard[opp.bat.row+1][opp.bat.col-1]=false;
						sunkBoard[opp.bat.row+1][opp.bat.col-1]=true;
						hitBoard[opp.bat.row+2][opp.bat.col-1]=false;
						sunkBoard[opp.bat.row+2][opp.bat.col-1]=true;
					}else if (downDist<3 && upDist>=3 && leftDist<3 && rightDist<3){
						opp.bat.dir=4;
						hitBoard[opp.bat.row-2][opp.bat.col-1]=false;
						sunkBoard[opp.bat.row-2][opp.bat.col-1]=true;
						hitBoard[opp.bat.row-3][opp.bat.col-1]=false;
						sunkBoard[opp.bat.row-3][opp.bat.col-1]=true;
						hitBoard[opp.bat.row-4][opp.bat.col-1]=false;
						sunkBoard[opp.bat.row-4][opp.bat.col-1]=true;
					}else if (downDist<3 && upDist<3 && leftDist>=3 && rightDist<3){
						opp.bat.dir=3;
						hitBoard[opp.bat.row-1][opp.bat.col-2]=false;
						sunkBoard[opp.bat.row-1][opp.bat.col-2]=true;
						hitBoard[opp.bat.row-1][opp.bat.col-3]=false;
						sunkBoard[opp.bat.row-1][opp.bat.col-3]=true;
						hitBoard[opp.bat.row-1][opp.bat.col-4]=false;
						sunkBoard[opp.bat.row-1][opp.bat.col-4]=true;
					}else if (downDist<3 && upDist<3 && leftDist<3 && rightDist>=3){
						opp.bat.dir=1;
						hitBoard[opp.bat.row-1][opp.bat.col]=false;
						sunkBoard[opp.bat.row-1][opp.bat.col]=true;
						hitBoard[opp.bat.row-1][opp.bat.col+1]=false;
						sunkBoard[opp.bat.row-1][opp.bat.col+1]=true;
						hitBoard[opp.bat.row-1][opp.bat.col+2]=false;
						sunkBoard[opp.bat.row-1][opp.bat.col+2]=true;
					}
				}
				if (!opp.des.isAlive && !opp.des.isFound){
					short downDist=hitScan(1,0,opp.des.row,opp.des.col);
					short upDist=hitScan(-1,0,opp.des.row,opp.des.col);
					short rightDist=hitScan(0,1,opp.des.row,opp.des.col);
					short leftDist=hitScan(0,-1,opp.des.row,opp.des.col);

					if (downDist>=2 && upDist<2 && leftDist<2 && rightDist<2){
						opp.des.dir=2;
						hitBoard[opp.des.row][opp.des.col-1]=false;
						sunkBoard[opp.des.row][opp.des.col-1]=true;
						hitBoard[opp.des.row+1][opp.des.col-1]=false;
						sunkBoard[opp.des.row+1][opp.des.col-1]=true;
					}else if (downDist<2 && upDist>=2 && leftDist<2 && rightDist<2){
						opp.des.dir=4;
						hitBoard[opp.des.row-2][opp.des.col-1]=false;
						sunkBoard[opp.des.row-2][opp.des.col-1]=true;
						hitBoard[opp.des.row-3][opp.des.col-1]=false;
						sunkBoard[opp.des.row-3][opp.des.col-1]=true;
					}else if (downDist<2 && upDist<2 && leftDist>=2 && rightDist<2){
						opp.des.dir=3;
						hitBoard[opp.des.row-1][opp.des.col-2]=false;
						sunkBoard[opp.des.row-1][opp.des.col-2]=true;
						hitBoard[opp.des.row-1][opp.des.col-3]=false;
						sunkBoard[opp.des.row-1][opp.des.col-3]=true;
					}else if (downDist<2 && upDist<2 && leftDist<2 && rightDist>=2){
						opp.des.dir=1;
						hitBoard[opp.des.row-1][opp.des.col]=false;
						sunkBoard[opp.des.row-1][opp.des.col]=true;
						hitBoard[opp.des.row-1][opp.des.col+1]=false;
						sunkBoard[opp.des.row-1][opp.des.col+1]=true;
					}
				}
				if (!opp.sub.isAlive && !opp.sub.isFound){
					short downDist=hitScan(1,0,opp.sub.row,opp.sub.col);
					short upDist=hitScan(-1,0,opp.sub.row,opp.sub.col);
					short rightDist=hitScan(0,1,opp.sub.row,opp.sub.col);
					short leftDist=hitScan(0,-1,opp.sub.row,opp.sub.col);

					if (downDist>=2 && upDist<2 && leftDist<2 && rightDist<2){
						opp.sub.dir=2;
						hitBoard[opp.sub.row][opp.sub.col-1]=false;
						sunkBoard[opp.sub.row][opp.sub.col-1]=true;
						hitBoard[opp.sub.row+1][opp.sub.col-1]=false;
						sunkBoard[opp.sub.row+1][opp.sub.col-1]=true;
					}else if (downDist<2 && upDist>=2 && leftDist<2 && rightDist<2){
						opp.sub.dir=4;
						hitBoard[opp.sub.row-2][opp.sub.col-1]=false;
						sunkBoard[opp.sub.row-2][opp.sub.col-1]=true;
						hitBoard[opp.sub.row-3][opp.sub.col-1]=false;
						sunkBoard[opp.sub.row-3][opp.sub.col-1]=true;
					}else if (downDist<2 && upDist<2 && leftDist>=2 && rightDist<2){
						opp.sub.dir=3;
						hitBoard[opp.sub.row-1][opp.sub.col-2]=false;
						sunkBoard[opp.sub.row-1][opp.sub.col-2]=true;
						hitBoard[opp.sub.row-1][opp.sub.col-3]=false;
						sunkBoard[opp.sub.row-1][opp.sub.col-3]=true;
					}else if (downDist<2 && upDist<2 && leftDist<2 && rightDist>=2){
						opp.sub.dir=1;
						hitBoard[opp.sub.row-1][opp.sub.col]=false;
						sunkBoard[opp.sub.row-1][opp.sub.col]=true;
						hitBoard[opp.sub.row-1][opp.sub.col+1]=false;
						sunkBoard[opp.sub.row-1][opp.sub.col+1]=true;
					}
				}
				if (!opp.pat.isAlive && !opp.pat.isFound){
					short downDist=hitScan(1,0,opp.pat.row,opp.pat.col);
					short upDist=hitScan(-1,0,opp.pat.row,opp.pat.col);
					short rightDist=hitScan(0,1,opp.pat.row,opp.pat.col);
					short leftDist=hitScan(0,-1,opp.pat.row,opp.pat.col);

					if (downDist>=1 && upDist<1 && leftDist<1 && rightDist<1){
						opp.pat.dir=2;
						hitBoard[opp.pat.row][opp.pat.col-1]=false;
						sunkBoard[opp.pat.row][opp.pat.col-1]=true;
					}else if (downDist<1 && upDist>=1 && leftDist<1 && rightDist<1){
						opp.pat.dir=4;
						hitBoard[opp.pat.row-2][opp.pat.col-1]=false;
						sunkBoard[opp.pat.row-2][opp.pat.col-1]=true;
					}else if (downDist<1 && upDist<1 && leftDist>=1 && rightDist<1){
						opp.pat.dir=3;
						hitBoard[opp.pat.row-1][opp.pat.col-2]=false;
						sunkBoard[opp.pat.row-1][opp.pat.col-2]=true;
					}else if (downDist<1 && upDist<1 && leftDist<1 && rightDist>=1){
						opp.pat.dir=1;
						hitBoard[opp.pat.row-1][opp.pat.col]=false;
						sunkBoard[opp.pat.row-1][opp.pat.col]=true;
					}
				}
			};

			void printBoard(){
				fprintf(stdout,"\n");
				for (short row=1; row<=10; row++){
					for (short col=1; col<=10; col++){
						if (!missBoard[row-1][col-1] && !hitBoard[row-1][col-1] && !sunkBoard[row-1][col-1]){
							fprintf(stdout,"O ");
						}else if(missBoard[row-1][col-1] && !hitBoard[row-1][col-1] && !sunkBoard[row-1][col-1]){
							fprintf(stdout,"M ");
						}else if(!missBoard[row-1][col-1] && hitBoard[row-1][col-1] && !sunkBoard[row-1][col-1]){
							fprintf(stdout,"H ");
						}else if(!missBoard[row-1][col-1] && !hitBoard[row-1][col-1] && sunkBoard[row-1][col-1]){
							fprintf(stdout,"S ");
						}else if(missBoard[row-1][col-1] && hitBoard[row-1][col-1] && !sunkBoard[row-1][col-1]){
							fprintf(stdout,"ERROR MH ");
						}else if(missBoard[row-1][col-1] && !hitBoard[row-1][col-1] && sunkBoard[row-1][col-1]){
							fprintf(stdout,"ERROR MS ");
						}else if(!missBoard[row-1][col-1] && hitBoard[row-1][col-1] && sunkBoard[row-1][col-1]){
							fprintf(stdout,"ERROR HS ");
						}else if(missBoard[row-1][col-1] && hitBoard[row-1][col-1] && sunkBoard[row-1][col-1]){
							fprintf(stdout,"ERROR MHS ");
						}else{
							fprintf(stdout,"LOGIC ERROR ");
						}
					}
					fprintf(stdout,"\n");
				}
			};
	};

	GameState game;

	char filename[256]="bensucks_folder/bensucks.txt";

	game.getHistory(filename);

	/*for (short gameNum=1; gameNum<=10000; gameNum++){
		game.reset();
		for (short move=1; move<=100; move++){
			game.pickMove();
			char buf[2];
			buf[0]=(char)(game.lastCol()+64);
			buf[1]=(char)(game.lastRow()+47);
			game.recordOppGuess(buf);
			game.recordMiss();
		}
	}*/

	while (game.isRunning()){
		fprintf(stdout,">");
		char buf[256];
		short junk;
		junk=fscanf(stdin, "%s", buf);

		if (buf[0] == 'N'){
			game.reset();
			junk=fscanf(stdin, "%s", buf);
			game.setOpponentName(buf);
			game.placeShips();
			game.printShips();
		}else if (buf[0] == 'F'){
			game.pickMove();
			game.printMove();
		}else if (buf[0] == 'H'){
			game.recordHit();
		}else if (buf[0] == 'M'){
			game.recordMiss();
		}else if (buf[0] == 'S'){
			junk=fscanf(stdin, "%s", buf);
			game.sink(buf);
		}else if (buf[0] == 'O'){
			junk=fscanf(stdin, "%s", buf);
			game.recordOppGuess(buf);
		}else if (buf[0] == 'W'){
			game.reset();
			game.printWin();
		}else if (buf[0] == 'L'){
			game.reset();
			game.printLoss();
		}else if (buf[0] == 'K'){
			game.reset();
			game.end();
		}else if (buf[0] == 'E'){
			game.reset();
			game.printError();
		}else{
			fprintf(stdout, "\n");
			fflush(stdout);
		}
	}

	game.setHistory(filename);

	return 0;
}
