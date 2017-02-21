import java.util.*;
import java.util.List;

public class MyBot {
    public static void main(String[] args) throws java.io.IOException {

        final InitPackage iPackage = Networking.getInit();
        final int myID = iPackage.myID;
        final GameMap gameMap = iPackage.map;
        final double[] coefficients = {-1.103294945996423,3.918117688144976,3.0415830054919297,0.0,-0.7884090872920998,23.347298508227667,-0.535230018936429,0.0,1.976484434923589,-4.858063166398838,7.22687101669685,0.0,1.1977584315469112,0.8023976004056277,-5.796682759613314,-0.0,-2.764784997382059,-5.795888087911079,-0.1660076405952977,1.0648777386999733,1.8057678861965198,18.703295991936052};
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
        Networking.sendInit("LearnBot");

        while(true) {
            Networking.updateFrame(gameMap);
            List<Move> moves = new ArrayList<Move>();
            int[][][] scores = new int[gameMap.width][gameMap.height][5];
            for (int y = 0; y < gameMap.height; y++) {
                for (int x = 0; x < gameMap.width; x++) {
                    final Location location = gameMap.getLocation(x, y);
                    final Site site = location.getSite();
                    if(site.owner == myID) {
                        scores[x][y][4] = site.strength;
                    }
                    else if(site.owner == 0)
                    {
                        scores[x][y][3] = site.strength;
                    }
                    else
                    {
                        scores[x][y][0] = site.strength;
                    }
                    scores[x][y][1] = site.production;
                    scores[x][y][2] = scores[x][y][0]+scores[x][y][3];
                }
            }
            double[][][][] dirscores = new double[gameMap.width][gameMap.height][4][22];
            int count = 0;
            int count2 = 0;
            for (int y = 1; y < gameMap.height; y++) {
                for (int x = 0; x < gameMap.width; x++) {
                    for (int y2 = 0; y2 < Math.min(gameMap.height/2,15); y2++) {
                        for (int x2 = -y2; x2 < y2; x2++) {
                            fill(x,y,x2,y2,3,Math.abs(y2)+Math.abs(x2),scores[x][y],gameMap.width,gameMap.height,dirscores);
                            count++;
                        }
                    }
                    if(count2 == 0)
                        count2 = count;
                    for (int y2 = 0; y2 < Math.min(15,gameMap.height/2); y2++) {
                        for (int x2 = -y2; x2 < y2; x2++) {
                            fill(x,y,x2,-y2,1,Math.abs(y2)+Math.abs(x2),scores[x][y],gameMap.width,gameMap.height,dirscores);
                        }
                    }
                    for (int x2 = 0; x2 < Math.min(15,gameMap.width/2); x2++) {
                        for (int y2 = -x2; y2 < x2; y2++) {
                            fill(x,y,x2,y2,2,Math.abs(y2)+Math.abs(x2),scores[x][y],gameMap.width,gameMap.height,dirscores);
                        }
                    }
                    for (int x2 = 0; x2 < Math.min(15,gameMap.width/2); x2++) {
                        for (int y2 = -x2; y2 < x2; y2++) {
                            fill(x,y,-x2,y2,0,Math.abs(y2)+Math.abs(x2),scores[x][y],gameMap.width,gameMap.height,dirscores);
                        }
                    }
                    //fill in the immediate scores
                    fill3(x,y,1,0,2,scores[x][y],gameMap.width,gameMap.height,dirscores);
                    fill2(x,y,1,1,2,scores[x][y],gameMap.width,gameMap.height,dirscores);
                    fill2(x,y,1,-1,2,scores[x][y],gameMap.width,gameMap.height,dirscores);
                    fill2(x,y,2,0,2,scores[x][y],gameMap.width,gameMap.height,dirscores);
                    fill3(x,y,0,1,3,scores[x][y],gameMap.width,gameMap.height,dirscores);
                    fill2(x,y,-1,1,3,scores[x][y],gameMap.width,gameMap.height,dirscores);
                    fill2(x,y,1,1,3,scores[x][y],gameMap.width,gameMap.height,dirscores);
                    fill2(x,y,0,2,3,scores[x][y],gameMap.width,gameMap.height,dirscores);
                    fill3(x,y,-1,0,0,scores[x][y],gameMap.width,gameMap.height,dirscores);
                    fill2(x,y,-2,0,0,scores[x][y],gameMap.width,gameMap.height,dirscores);
                    fill2(x,y,-1,-1,0,scores[x][y],gameMap.width,gameMap.height,dirscores);
                    fill2(x,y,-1,1,0,scores[x][y],gameMap.width,gameMap.height,dirscores);
                    fill3(x,y,0,-1,1,scores[x][y],gameMap.width,gameMap.height,dirscores);
                    fill2(x,y,0,-2,1,scores[x][y],gameMap.width,gameMap.height,dirscores);
                    fill2(x,y,-1,-1,1,scores[x][y],gameMap.width,gameMap.height,dirscores);
                    fill2(x,y,1,-1,1,scores[x][y],gameMap.width,gameMap.height,dirscores);
                }
            }
            for (int y = 0; y < gameMap.height; y++) {
                for (int x = 0; x < gameMap.width; x++) {
                    final Location location = gameMap.getLocation(x, y);
                    final Site site = location.getSite();
                    if(site.owner == myID) {
                        int id = 0;
                        int score = -99999;
                        for(int i = 0; i < 4; i++)
                        {
                            int c = 0;
                            for(int j = 0; j < 5; j++)
                            {
                                dirscores[x][y][i][4*j]/=count2;
                                dirscores[x][y][i][4*j+1]/=10;
                                dirscores[x][y][i][4*j+2]/=4;
                            }
                            for(int j = 0; j < 22; j++)
                            {
                                c += coefficients[j]*dirscores[x][y][i][j];
                            }
                            if(c > score)
                            {
                                id = i;
                                score = c;
                            }
                        }
                        if(site.strength==0)
                            moves.add(new Move(location, Direction.STILL));
                        else if(site.strength==255||score + (site.strength-128) * coefficients[20] + 10*coefficients[21] > 0)
                        {
                            moves.add(new Move(location, direcs[id]));
                        }
                        else
                            moves.add(new Move(location, Direction.STILL));
                    }
                }
            }
            Networking.sendFrame(moves);
        }
    }
    private static void fill(int x, int y, int dx, int dy, int side, int distance, int[] values, int width, int height, double[][][][] scores)
    {
        int x2 = x + dx;
        int y2 = y + dy;
        while(x2<0)
            x2+=width;
        while(y2<0)
            y2+=height;
        x2 %= width;
        y2 %= height;
        for(int i = 0; i < values.length; i++)
        {
            scores[x2][y2][side][4*i] += values[i];
            scores[x2][y2][side][4*i+1] += values[i]*1.0/distance;
        }
    }
    private static void fill2(int x, int y, int dx, int dy, int side, int[] values, int width, int height, double[][][][] scores)
    {
        int x2 = x + dx;
        int y2 = y + dy;
        while(x2<0)
            x2+=width;
        while(y2<0)
            y2+=height;
        x2 %= width;
        y2 %= height;
        for(int i = 0; i < values.length; i++)
        {
            scores[x2][y2][side][4*i+2] += values[i];
        }
    }
    private static void fill3(int x, int y, int dx, int dy, int side, int[] values, int width, int height, double[][][][] scores)
    {
        fill2(x,y,dx,dy,side,values,width,height,scores);
        int x2 = x + dx;
        int y2 = y + dy;
        while(x2<0)
            x2+=width;
        while(y2<0)
            y2+=height;
        x2 %= width;
        y2 %= height;
        for(int i = 0; i < values.length; i++)
        {
            scores[x2][y2][side][3*i+3] += values[i];
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
