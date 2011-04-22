package cdmuhlb.battleship;

import x10.util.Random;

public class GameState {
	public val tState : TournamentState;
	public val rng = new Random();
	
	public def this(tState : TournamentState) {
		this.tState = tState;
	}
}