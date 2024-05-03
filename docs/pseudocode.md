# The pseudocode

```js
function minimax(position, depth, maximizingPlayerPlaying, alpha, beta)
    if depth == 0 or position == game over
        return static eval of position

    if maximizingPlayerPlaying
        max_eval = -infinity

        for child in position
            child_eval = minimax(child, depth - 1, false)
            max_eval = max(max_eval, child_eval)

            alpha = max(alpha, child_eval)
            if beta <= alpha
                break

        return max_eval
    
    else
        min_eval = +infinity
        
        for child in position
            child_eval = minimax(child, depth - 1, true)
            min_eval = min(min_eval, child_eval)

            beta = min(beta, child_eval)
            if beta <= alpha
                break

        return min_eval

minimax(current_position, 3, true, -∞, +∞)
```
