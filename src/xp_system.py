

def calc_xp(reviews: int, retention_rate: float):
    """Calculate XP from reviews and retention rate

    Args:
        reviews (int): number of reviews
        retention_rate (float): retention rate

    Returns:
        int: xp
    """
    
    return round(reviews * retention_rate)
