import java.io.Console;
import java.util.Arrays;
import java.io.IOException;
import java.util.Random;


class javabattle
{
	public static void guess() {
		Console c = System.console();

		Random generator = new Random();

		int let = 65 + generator.nextInt(10);
		int num = generator.nextInt(10);

		c.format("%c%d\n", let, num);
	}
	public static void newboard() {
		Console c = System.console();
		c.format("A0D B0D C0D D0D E0D\n");
	}
	public static void main(String args[])
	{
		Console c = System.console();
		int running = 1;
		while(running==1) {
			String inp = c.readLine(">");
			

			if (inp.charAt(0) == 'K') {
				running = 0;
			} else if (inp.charAt(0) == 'F') {
				guess();
			} else if (inp.charAt(0) == 'N') {
				newboard();
			} else {
				c.format("\n");
			}
		}
	}

}
