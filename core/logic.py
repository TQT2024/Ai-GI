from collections import deque

# note:
# Bit 0: người lái (B)
# Bit 1: sói (W)
# Bit 2: dê (G)
# Bit 3: bắp cải (C)
# Giá trị bit 0 => bờ trái, 1 => bờ phải
# first state: 0 (0000), final state: 15 (1111)

def is_valid(state: int) -> bool:
    """
    Check tính hợp lệ của state.
    Với mỗi bờ (0 và 1), nếu:
      - Sói và dê cùng bờ mà không có người lái và bắp cải thì không hợp lệ.
      - Dê và bắp cải cùng bờ mà không có người lái đò và sói thì không hợp lệ.
    """
    # Lấy giá trị của từng obj
    boatman   = (state >> 0) & 1
    wolf    = (state >> 1) & 1
    goat    = (state >> 2) & 1
    cabbage = (state >> 3) & 1

    for bank in (0, 1):
        # Nếu sói và dê ở cùng bờ, nhưng nguười lái và bắp cải không ở bờ đó
        if wolf == bank and goat == bank and (boatman != bank and cabbage != bank):
            return False
        # Nếu dê và bắp cải ở cùng bờ, nhưng người lái và sói không ở bờ đó
        if goat == bank and cabbage == bank and (boatman != bank and wolf != bank):
            return False
    return True

def get_possible_moves(state: int):
    """
    Init các bước đi hợp lệ từ state hiện tại.
    Mỗi bước đi: người lái luôn chuyển qua bờ còn lại,
    và có thể chọn chuyển cùng 0, 1 hoặc 2 đối tượng (W, G, C) đang cùng bờ với người lái.
    """
    moves = []
    boatman_bank = state & 1  # bờ 1 của người lái (bit 0)
    
    # List các obj (name, bit pos)
    entities = [('W', 1), ('G', 2), ('C', 3)]
    # Chỉ lấy các obj đang cùng bờ với boatman
    available = [entity for entity in entities if ((state >> entity[1]) & 1) == boatman_bank]
    
    # combination: 0 khách, 1 khách hoặc 2 khách
    subsets = [[]]
    for e in available:
        subsets.append([e])
    if len(available) >= 2:
        for i in range(len(available)):
            for j in range(i+1, len(available)):
                subsets.append([available[i], available[j]])
                
    # Với mỗi combin, đảo bit của boatmman và các obj được chọn
    for subset in subsets:
        new_state = state
        # Đảo bit của boatman để chuyển bờ
        new_state ^= 1  # Flip bit 0
        for _, bit in subset:
            new_state ^= (1 << bit)  # Flip bit tương ứng
        if is_valid(new_state):
            moves.append((new_state, [name for name, _ in subset]))
    return moves

def bfs_solution(start_state: int):
    """
    DÙng BFS để giải quyết bài toán từ first state đến final state (15)
    Trả về list các bước đi dưới dạng: (state, list obj chuyển).
    """
    goal_state = 15  # 1111
    queue = deque()
    queue.append((start_state, []))
    visited = {start_state}
    
    while queue:
        state, path = queue.popleft()
        if state == goal_state:
            return path + [(state, [])]
        for next_state, moved in get_possible_moves(state):
            if next_state not in visited:
                visited.add(next_state)
                queue.append((next_state, path + [(state, moved)]))
    return None

# Module test để chạy single
if __name__ == '__main__':
    start = 0  # 0000: tất cả ở bờ trái
    sol = bfs_solution(start)
    if sol:
        print("Lời giải:")
        for s, moved in sol:
            print(f"Trạng thái: {s:04b}, chuyển: {moved}")
    else:
        print("Không giải quyết được")
