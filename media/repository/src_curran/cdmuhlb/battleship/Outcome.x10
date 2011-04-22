package cdmuhlb.battleship;

public struct Outcome {
	private val id : Int;
	private def this(id : Int) {
		this.id = id;
	}
	
	public def serialize() : String {
		if (this == NONE) {
			return "";
		} else if (this == HIT) {
			return "H";
		} else if (this == MISS) {
			return "M";
		} else if (this == SUNK_CARRIER) {
			return "S " + Ship.CARRIER.serialize();
		} else if (this == SUNK_BATTLESHIP) {
			return "S " + Ship.BATTLESHIP.serialize();
		} else if (this == SUNK_DESTROYER) {
			return "S " + Ship.DESTROYER.serialize();
		} else if (this == SUNK_SUBMARINE) {
			return "S " + Ship.SUBMARINE.serialize();
		} else if (this == SUNK_PATROL_BOAT) {
			return "S " + Ship.PATROL_BOAT.serialize();
		} else {
			// Should not reach here
			return null;
		}
	}
	
	public static def deserialize(str : String) : Outcome {
		if (str.equals("")) {
			return NONE;
		} else if (str.equals("H")) {
			return HIT;
		} else if (str.equals("M")) {
			return MISS;
		} else if (str.equals("S " + Ship.CARRIER.serialize())) {
			return SUNK_CARRIER;
		} else if (str.equals("S " + Ship.BATTLESHIP.serialize())) {
			return SUNK_BATTLESHIP;
		} else if (str.equals("S " + Ship.DESTROYER.serialize())) {
			return SUNK_DESTROYER;
		} else if (str.equals("S " + Ship.SUBMARINE.serialize())) {
			return SUNK_SUBMARINE;
		} else if (str.equals("S " + Ship.PATROL_BOAT.serialize())) {
			return SUNK_PATROL_BOAT;
		} else {
			throw new IllegalArgumentException();
		}
	}
	
	public static val NONE = Outcome(0);
	public static val HIT = Outcome(1);
	public static val MISS = Outcome(2);
	public static val SUNK_CARRIER = Outcome(3);
	public static val SUNK_BATTLESHIP = Outcome(4);
	public static val SUNK_DESTROYER = Outcome(5);
	public static val SUNK_SUBMARINE = Outcome(6);
	public static val SUNK_PATROL_BOAT = Outcome(7);
}