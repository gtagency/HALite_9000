import java.util.*;
import java.util.List;

public class MyBot {
    public static void main(String[] args) throws java.io.IOException {

        final InitPackage iPackage = Networking.getInit();
        final int myID = iPackage.myID;
        final GameMap gameMap = iPackage.map;
        int[][] dirs = {{1,0},
        {0,1},
        {-1,0},
        {0,-1}
        };
        Direction[] direcs = {
        Direction.EAST,
        Direction.SOUTH,
        Direction.WEST,
        Direction.NORTH,
        Direction.STILL
        };
        int numb = 0;
        for (int y = 0; y < gameMap.height; y++) {
            for (int x = 0; x < gameMap.width; x++) {
                numb+=gameMap.getLocation(x, y).getSite().strength;
            }
        }
        numb/=(gameMap.width*gameMap.height*5);
        int time = gameMap.width*gameMap.height/5;
        Networking.sendInit("MyJavaBot4");

        int myX = -1;
        int myY = -1;
        int count = 0;
        while(true) {
            count++;
            if(count%time==0)
                numb++;
            List<Move> moves = new ArrayList<Move>();
            
            Networking.updateFrame(gameMap);
            int[][] scores = new int[gameMap.width][gameMap.height];
            LinkedList<Integer[]> list = new LinkedList<>();
            for (int y = 0; y < gameMap.height; y++) {
                for (int x = 0; x < gameMap.width; x++) {
                    final Location location = gameMap.getLocation(x, y);
                    final Site site = location.getSite();
                    if(site.owner == myID) {
                        for(int i = 0; i < 4; i++)
                        {
                            Site side = getSite(gameMap,x,y,dirs[i]);
                            if(side.owner!=myID)
                                if(256-side.strength>scores[x][y])
                                    scores[x][y] = 256-side.strength;
                        }
                    }
                    else if(site.strength < numb)
                        list.add(new Integer[]{x,y});
                    if(scores[x][y]>0)
                    {
                        //list.add(new Integer[]{x,y});
                    }
                }
            }
            for (int y = 0; y < gameMap.height; y++) {
                for (int x = 0; x < gameMap.width; x++) {
                    final Location location = gameMap.getLocation(x, y);
                    final Site site = location.getSite();
                    if(site.owner == myID) {
                        if(scores[x][y]==0)
                        {
                            int[] vals = getMin(x,y,list,gameMap.height,gameMap.width);
                            if(site.strength > 1 && vals[0]+vals[1]+site.strength >= numb+5)
                            {
                                if(Math.abs(vals[0])>Math.abs(vals[1]))
                                {
                                    if(vals[0]>0)
                                        moves.add(new Move(location, Direction.EAST));
                                    else
                                        moves.add(new Move(location, Direction.WEST));
                                }
                                else
                                {
                                    if(vals[1]>0)
                                        moves.add(new Move(location, Direction.SOUTH));
                                    else
                                        moves.add(new Move(location, Direction.NORTH));
                                }
                            }
                            else
                                moves.add(new Move(location, Direction.STILL));
                        }
                        else
                        {
                            int dir = 4;
                            LinkedList<Integer> directs = new LinkedList<>();
                            if(256 - site.strength < scores[x][y])
                            {
                                for(int i = 0; i < 4; i++)
                                {
                                    Site side = getSite(gameMap,x,y,dirs[i]);
                                    if(side.owner!=myID)
                                        if(256-side.strength==scores[x][y])
                                            directs.add(i);
                                }
                                moves.add(new Move(location, direcs[directs.get((int)(Math.random()*directs.size()))]));
                            }
                            else
                                moves.add(new Move(location, Direction.STILL));
                        }
                    }
                }
            }
            Networking.sendFrame(moves);
        }
    }
    private static Site getSite(GameMap map, int x, int y, int... dir)
    {
        return map.getLocation((map.width+dir[0]+x)%map.width,(map.height+dir[1]+y)%map.height).getSite();
    }
    private static int[] getMin(int x, int y, LinkedList<Integer[]> list, int height, int width)
    {
        int[] res = {999999,999999};
        for(Integer[] i: list)
            if(mindist(i[0]-x,width)+mindist(i[1]-y,height) < Math.abs(res[0]) + Math.abs(res[1]))
            {
                res[0]=Math.abs(i[0]-x) < Math.abs(width-(i[0]-x))?i[0]-x:width-(i[0]-x);
                res[1]=Math.abs(i[1]-y) < Math.abs(height-(i[1]-y))?i[1]-y:height-(i[1]-y);
            }
        return res;
    }
    private static int mindist(int dif, int max)
    {
        dif = Math.abs(dif);
        return dif < max-dif?dif:max-dif;
    }
}
