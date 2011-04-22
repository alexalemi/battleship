package cdmuhlb.battleship;

public class Deployment {
	public val ship : Ship;
	public val pos : Position;
	public val vertical : Boolean;
	
	public def this(ship : Ship, pos : Position, vertical : Boolean) {
		if ((vertical && (pos.row + ship.length() > 10)) ||
				(!vertical && (pos.col + ship.length() > 10))) {
			throw new IllegalArgumentException();
		}
		this.ship = ship;
		this.pos = pos;
		this.vertical = vertical;
	}
	
	public def serialize() : String {
		return pos.serialize() + (vertical ? "D" : "R");
	}
	
	public def intersects(that : Deployment) : Boolean {
		val x1 = pos.col;
		val y1 = pos.row;
		val w1 = vertical ? 1 : ship.length();
		val h1 = vertical ? ship.length() : 1;
		val x2 = that.pos.col;
		val y2 = that.pos.row;
		val w2 = that.vertical ? 1 : that.ship.length();
		val h2 = that.vertical ? that.ship.length() : 1;
		
		return (x2+w2 > x1) && (x2 < x1+w1) && (y2+h2 > y1) && (y2 < y1+h1);
	}
	
	public def contains(pt : Position) {
		if (vertical) {
			return (pt.col == pos.col) && (pt.row >= pos.row) &&
					(pt.row < pos.row+ship.length());
		} else {
			return (pt.row == pos.row) && (pt.col >= pos.col) &&
					(pt.col < pos.col+ship.length());
		}
	}
}