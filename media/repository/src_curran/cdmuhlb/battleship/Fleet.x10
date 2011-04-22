package cdmuhlb.battleship;

public class Fleet {
	val carrier : Deployment;
	val battleship : Deployment;
	val destroyer : Deployment;
	val submarine : Deployment;
	val patrolBoat : Deployment;
	
	public def this(carrier : Deployment, battleship : Deployment,
			destroyer : Deployment, submarine : Deployment,
			patrolBoat : Deployment) {
		if ((carrier.ship != Ship.CARRIER) || (battleship.ship != Ship.BATTLESHIP) ||
				(destroyer.ship != Ship.DESTROYER) || (submarine.ship != Ship.SUBMARINE) ||
				(patrolBoat.ship != Ship.PATROL_BOAT)) {
			throw new IllegalArgumentException();
		}
		if (carrier.intersects(battleship) || carrier.intersects(destroyer) ||
				carrier.intersects(submarine) || carrier.intersects(patrolBoat) ||
				battleship.intersects(destroyer) || battleship.intersects(submarine) ||
				battleship.intersects(patrolBoat) || destroyer.intersects(submarine) ||
				destroyer.intersects(patrolBoat) || submarine.intersects(patrolBoat)) {
			throw new IllegalArgumentException();
		}
		this.carrier = carrier;
		this.battleship = battleship;
		this.destroyer = destroyer;
		this.submarine = submarine;
		this.patrolBoat = patrolBoat;
	}
	
	public def serialize() : String {
		return carrier.serialize() + " " + battleship.serialize() + " " +
				destroyer.serialize() + " " + submarine.serialize() + " " +
				patrolBoat.serialize();
	}
	
	public static def deserialize(str : String) : Fleet {
		if (str.length() != 19) {
			throw new IllegalArgumentException();
		}
		if (((str(2) != 'D') && (str(2) != 'R')) || ((str(6) != 'D') && (str(6) != 'R')) ||
				((str(10) != 'D') && (str(10) != 'R')) || ((str(14) != 'D') && (str(14) != 'R')) ||
				((str(18) != 'D') && (str(18) != 'R'))) {
			throw new IllegalArgumentException();
		}
		val c = new Deployment(Ship.CARRIER, Position.deserialize(str.substring(0, 2)), str(2) == 'D');
		val b = new Deployment(Ship.BATTLESHIP, Position.deserialize(str.substring(4, 6)), str(6) == 'D');
		val d = new Deployment(Ship.DESTROYER, Position.deserialize(str.substring(8, 10)), str(10) == 'D');
		val s = new Deployment(Ship.SUBMARINE, Position.deserialize(str.substring(12, 14)), str(14) == 'D');
		val p = new Deployment(Ship.PATROL_BOAT, Position.deserialize(str.substring(16, 18)), str(18) == 'D');
		return new Fleet(c, b, d, s, p);
	}
	
	public def contains(pt : Position) : Boolean {
		return carrier.contains(pt) || battleship.contains(pt) ||
				destroyer.contains(pt) || submarine.contains(pt) ||
				patrolBoat.contains(pt);
	}
	
	public def whichContains(pt : Position) : Deployment {
		if (carrier.contains(pt)) {
			return carrier;
		} else if (battleship.contains(pt)) {
			return battleship;
		} else if (destroyer.contains(pt)) {
			return destroyer;
		} else if (submarine.contains(pt)) {
			return submarine;
		} else if (patrolBoat.contains(pt)) {
			return patrolBoat;
		} else {
			return null;
		}
	}
	
	public def printBoard() {
		Console.OUT.println("     A   B   C   D   E   F   G   H   I   J  ");
		Console.OUT.println("   -----------------------------------------");
		for (var i:Int=0; i < 10; ++i) {
			Console.OUT.print(" " + i + " |");
			for (var j:Int=0; j < 10; ++j) {
				Console.OUT.print(" " + (contains(Position(j, i)) ? "X" : " ") + " |");
			}
			Console.OUT.println();
			Console.OUT.println("   -----------------------------------------");
		}
	}
}