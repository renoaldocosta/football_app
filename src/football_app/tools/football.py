from statsbombpy import sb  # type: ignore

def get_match_details_match_id(match_id: int) -> dict:
    """
    Get the details of a specific match using the match ID.
    Args:
        match_id (int): The unique identifier of the match.
        
    Returns:
        dict: The details of the match.
    """
    raw_data = sb.events(match_id=match_id)  # type: ignore
    return raw_data


if __name__ == "__main__":
    match_id = 22949
    match_data = get_match_details_match_id(match_id)
    print(match_data)