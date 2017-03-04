import scala.util.Random
object QLearner {

}

class QLearner() {
  val gamma = 0.6;
  var rand = Random
  var Q = Array.ofDim[Double](900, 900)
  def getModel(R: Array[Array[Int]], walks: Int): Array[Array[Double]] = {
    for (i <- 1 to walks) {
      var state = rand.nextInt(R.length)
      var iterating = true
      var iters = 0;
      while (iterating) {
        var action_space = 
          for (action <- List.range(0, 900) if R(state)(action) > -1) yield action
        var action = action_space(rand.nextInt(action_space.length))
        var max_lookahead = 
          (for (value <- Q(action) if value > -1) yield {value}).reduceLeft(_ max _)
        Q(state)(action) = R(state)(action) + gamma * max_lookahead
        if (iters == 100) {
          iterating = false;
        } else {
          iters = iters + 1;
        }
      }
    }
    Q //scala is actually just dark dark magic
  }
}
