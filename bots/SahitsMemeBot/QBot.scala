import scala.util.Random
object QBot extends BotFactory {
  var ql = new QLearner()
  var R = Array.ofDim[Int](900,900)
  def state(height: Int, x: Int, y:Int) = (height * x) + y
  def main(args: Array[String]): Unit = {
    Runner.run("WhatWouldSimpkinsDo", this)
    var grid = Env.readInit()
    var height = grid.getHeight
    var width = grid.getWidth
    //magic happens here
    for {
      site <- grid.getSites
    } yield {
        //scala doesn't support overloading of % :(
        //TODO make this more memory efficient
        var down = (site.location.y + 1) % height
        var right = (site.location.x + 1) % width
        var left = site.location.x - 1
        if (left < 0) {
          left = width - 1
        }
        var up = site.location.x - 1
        if (up < 0) {
          up = height - 1
        }
        Array.tabulate(grid.getWidth, grid.getHeight)((x,y) => (-1))
        R(state(height, site.location.x, site.location.y))(state(height, site.location.x, up)) = grid.getSite(site.location.x, up).location.production 
        R(state(height, site.location.x, site.location.y))(state(height, site.location.x, down)) = grid.getSite(site.location.x, down).location.production
        R(state(height, site.location.x, site.location.y))(state(height, left, site.location.y)) = grid.getSite(left, site.location.y).location.production
        R(state(height, site.location.x, site.location.y))(state(height, right, site.location.y)) = grid.getSite(right, site.location.y).location.production
    }
    ql.getModel(R, 500)
  }

  
  override def make(id: Int): Bot = new QBot(id, ql)
}

class QBot(myId: Int, ql: QLearner) extends Bot {
  var Q = Array.ofDim[Int](30, 30)
  var R = Array.ofDim[Int](30, 30)
  override def getMoves(grid: Grid): Iterable[Move] = {
    for {
      site <- grid.getSites
    } yield {
      
    }
    var rand = Random
    val moves = Array(0, 1, 4)
    for {
      site <- grid.getMine(myId)
    } yield {
      for (neighbor <- grid.getNeighbors(site.location)) {
        if (neighbor.site.occupant.id != myId 
          && neighbor.site.occupant.strength < site.occupant.strength) {
          Move(site.location, neighbor.direction);
        }
      }
      if (site.occupant.strength < 5 * site.location.production) {
        Move(site.location, new Direction(0))
      } else {
        Move(site.location, new Direction(moves(rand.nextInt(3))))
      }
    }
  }
}
