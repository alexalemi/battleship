package cdmuhlb.battleship;

public class Driver {
    public static def main(args: Array[String](1)) {
        /*val d1 = new Deployment(Ship.CARRIER, Position(3,3), false);
        val d2 = new Deployment(Ship.SUBMARINE, Position.deserialize("H4"), true);
        Console.OUT.println(d1.ship.name() + ": " + d1.serialize());
        Console.OUT.println(d2.ship.name() + ": " + d2.serialize());
        Console.OUT.println("Intersection? " + d1.intersects(d2) + " / " + d2.intersects(d1));
        Console.OUT.println("Hits? " + d1.contains(Position(3,3)) + ", " +
        		d1.contains(Position.deserialize("H3")) + ", " +
        		d1.contains(Position.deserialize("H4")));
        
        val f1 = Fleet.deserialize("A0D B0D C0D D0D E6R");
        Console.OUT.println(f1.serialize());
        
        f1.printBoard();*/
        
        val io = new IOHandler();
        val th = new TournamentHandler(io);
        th.handleInput(io.readInput());
    }
}