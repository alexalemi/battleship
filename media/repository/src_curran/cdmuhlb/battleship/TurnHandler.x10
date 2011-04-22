package cdmuhlb.battleship;

import x10.util.Random;

public class TurnHandler {
	private val gState : GameState;
	private val io : IOHandler;
	private var shotFired : Boolean = false;
	private var posFired : Position;
	private var outcomeReceived : Boolean = false;
	private var outcome : Outcome;
	private var opponentReceived : Boolean = false;
	private var opponentPos : Position;
	
	public def this(gState : GameState) {
		this.gState = gState;
		this.io = gState.tState.io;
	}
	
	public def handleInput(var input : String) : String {
		/* Handle Firing */
		if (!input.equals("F")) {
			throw new IllegalArgumentException();
		}
		// set posFired to next guess
		posFired = Position(gState.rng.nextInt(10), gState.rng.nextInt(10));
		io.writeOutput(posFired.serialize());
		shotFired = true;
		
		/* Handle Outcome */
		input = io.readInput();
		if ((input(0) != 'H') && (input(0) != 'M') && (input(0) != 'S')) {
			if (!input.equals("E")) {
				Console.ERR.println("Unexpected outcome in TurnHandler: " + input);
			}
			return input;
		}
		outcome = Outcome.deserialize(input);
		outcomeReceived = true;
		// Update game state
		
		/* Handle Opponent's Guess */
		input = io.readInput();
		if (input(0) != 'O') {
			// Assume opponent made an error, and this is the game result.
			return input;
		}
		opponentPos = Position.deserialize(input.substring(2));
		opponentReceived = true;
		// Update opponent state
		
		/* Return next command */
		input = io.readInput();
		return input;
	}
}