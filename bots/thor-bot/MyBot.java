import java.util.*;
import java.util.List;

public class MyBot {
    public static void main(String[] args) throws java.io.IOException {

        final InitPackage iPackage = Networking.getInit();
        final int myID = iPackage.myID;
        final GameMap gameMap = iPackage.map;

        Networking.sendInit("MyJavaBot");

        int myX = -1;
        int myY = -1;
        while(true) {
            List<Move> moves = new ArrayList<Move>();
            
            Networking.updateFrame(gameMap);

            for (int y = 0; y < gameMap.height; y++) {
                for (int x = 0; x < gameMap.width; x++) {
                    final Location location = gameMap.getLocation(x, y);
                    final Site site = location.getSite();
                    if(site.owner == myID) {
                        if(myX == -1)
                        {
                            myX = x;
                            myY = y;
                        }
                        int tempX = myX;
                        int tempY = myY;
                        if(x == 0 || x == gameMap.width)
                            tempX = x;
                        if(y == 0 || y == gameMap.height)
                            tempX = y;
                        moves.add(new Move(location, getDirection(tempX,tempY,x,y,site.strength, gameMap, myID)));
                    }
                }
            }
            Networking.sendFrame(moves);
        }
    }
    private static Direction getDirection(int myX, int myY, int x, int y,int size, GameMap gameMap, int myID)
    {
        int dx = x - myX;
        int dy = y - myY;
        LinkedList<Direction> possibilities = new LinkedList<Direction>();
        for(int i = 0; i < 3; i++)
        {
            if(gameMap.getLocation((x+1)%gameMap.width,y).getSite().owner!=myID)
                possibilities.add(Direction.EAST);
            if(gameMap.getLocation((x-1+gameMap.width)%gameMap.width,y).getSite().owner!=myID)
                possibilities.add(Direction.WEST);
            if(gameMap.getLocation(x,(y+1)%gameMap.height).getSite().owner!=myID)
                possibilities.add(Direction.SOUTH);
            if(gameMap.getLocation(x,(y-1+gameMap.height)%gameMap.height).getSite().owner!=myID)
                possibilities.add(Direction.NORTH);
        }
        for(int i = 0; i < 20*(100-size); i++)
            possibilities.add(Direction.STILL);
        if(dy > 0)
            possibilities.add(Direction.SOUTH);
        else if(dy < 0)
            possibilities.add(Direction.NORTH);
        else
        {
            possibilities.add(Direction.SOUTH);
            possibilities.add(Direction.NORTH);
        }
        if(dx > 0)
            possibilities.add(Direction.EAST);
        else if(dy < 0)
            possibilities.add(Direction.WEST);
        else
        {
            possibilities.add(Direction.WEST);
            possibilities.add(Direction.EAST);
        }
        return possibilities.get((int)(Math.random()*possibilities.size()));
    }
}
