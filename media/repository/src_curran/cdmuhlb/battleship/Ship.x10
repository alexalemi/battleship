package cdmuhlb.battleship;

public abstract class Ship {
	public abstract def name() : String;
	public abstract def length() : Int;
	public abstract def serialize() : String;
	
	public static val CARRIER = new Carrier();
	public static val BATTLESHIP = new Battleship();
	public static val DESTROYER = new Destroyer();
	public static val SUBMARINE = new Submarine();
	public static val PATROL_BOAT = new PatrolBoat();
	
	public static def deserialize(str : String) : Ship {
		if (str.equals("C")) {
			return CARRIER;
		} else if (str.equals("B")) {
			return BATTLESHIP;
		} else if (str.equals("D")) {
			return DESTROYER;
		} else if (str.equals("S")) {
			return SUBMARINE;
		} else if (str.equals("P")) {
			return PATROL_BOAT;
		} else {
			throw new IllegalArgumentException();
		}
	}
	
	private static class Carrier extends Ship {
		public def name() = "Carrier";
		public def length() = 5;
		public def serialize() = "C";
		//public def equals(that:Any) = that instanceof Carrier;
		//public def hashCode() = name().hashCode(); 
	}
	
	private static class Battleship extends Ship {
		public def name() = "Battleship";
		public def length() = 4;
		public def serialize() = "B";
		//public def equals(that:Any) = that instanceof Battleship;
		//public def hashCode() = name().hashCode(); 
	}
	
	private static class Destroyer extends Ship {
		public def name() = "Destroyer";
		public def length() = 3;
		public def serialize() = "D";
		//public def equals(that:Any) = that instanceof Destroyer;
		//public def hashCode() = name().hashCode(); 
	}
	
	private static class Submarine extends Ship {
		public def name() = "Submarine";
		public def length() = 3;
		public def serialize() = "S";
		//public def equals(that:Any) = that instanceof Submarine;
		//public def hashCode() = name().hashCode(); 
	}
	
	private static class PatrolBoat extends Ship {
		public def name() = "Patrol Boat";
		public def length() = 2;
		public def serialize() = "P";
		//public def equals(that:Any) = that instanceof PatrolBoat;
		//public def hashCode() = name().hashCode(); 
	}
}