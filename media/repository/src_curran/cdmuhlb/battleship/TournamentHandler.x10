package cdmuhlb.battleship;

public class TournamentHandler {
	private val tState : TournamentState;
	
	public def this(io : IOHandler) {
		this.tState = new TournamentState(io);
	}
	
	public def handleInput(var input : String) : String {
		while (input.startsWith("N")) {
			val opponent = input.substring(2);
			val game = new GameHandler(tState);
			input = game.handleInput(input);
		}
		
		if (!input.equals("K")) {
			Console.ERR.println("Unexpected command in TournamentHandler: " + input);
		}
		return input;
	}
}