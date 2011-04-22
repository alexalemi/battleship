package cdmuhlb.battleship;

public class GameHandler {
	private var result : Int = 0; // Pending, Win, Loss, Error
	private val gState : GameState;
	private val io : IOHandler;
	private var myFleet : Fleet;
	
	public def this(tState : TournamentState) {
		this.gState = new GameState(tState);
		io = tState.io;
	}
	
	public def handleInput(var input : String) : String {
		/* Handle new game */
		if (!input.startsWith("N")) {
			throw new IllegalArgumentException();
		}
		// set myFleet to new board config
		myFleet = Fleet.deserialize("A0D B0D C0D D0D E6R");
		io.writeOutput(myFleet.serialize());
		
		/* Get first command */
		input = io.readInput();
		
		/* Loop over turns */
		while (input.equals("F")) {
			val turn = new TurnHandler(gState);
			input = turn.handleInput(input);
		}
		
		/* Handle result */
		if (input.equals("W")) {
			result = 1;
		} else if (input.equals("L")) {
			result = 2;
		} else if (input.equals("E")) {
			result = 3;
		} else {
			Console.ERR.println("Unexpected result in GameHandler: " + input);
			return input;
		}
		
		/* Return next command (N, K) */
		input = io.readInput();
		return input;
	}
}