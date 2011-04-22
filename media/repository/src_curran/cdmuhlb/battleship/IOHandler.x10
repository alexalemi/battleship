package cdmuhlb.battleship;

public class IOHandler {
	private val ioOut = Console.OUT;
	private val ioIn = Console.IN;
	
	private def writePrompt() {
		ioOut.print(">");
		ioOut.flush();
	}
	
	public def writeOutput(str : String) {
		ioOut.println(str);
		ioOut.flush();
	}
	
	public def readInput() : String {
		writePrompt();
		return ioIn.readLine().trim();
	}
}