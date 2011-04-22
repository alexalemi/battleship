package cdmuhlb.battleship;

public struct Position {
	public val row : Int;
	public val col : Int;
	
	public def this(col:Int, row:Int) {
		if ((row < 0) || (row > 9) || (col < 0) || (col > 9)) {
			throw new IllegalArgumentException();
		}
		this.row = row;
		this.col = col;
	}
	
	public def serialize() : String {
		return ('A' + col).toString() + row.toString();
	}
	
	public static def deserialize(str : String) : Position {
		if (str.length() != 2) {
			throw new IllegalArgumentException();
		}
		return Position(str(0) - 'A', Int.parse(str.substring(1)));
	}
}