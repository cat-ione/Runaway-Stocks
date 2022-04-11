def flip(**kwargs):
    player = kwargs["player"]
    player.reverse = not player.reverse

barrier_powers = {
    flip: 1
}