import cv2
import numpy as np

# Adaptive threshold levels
BKG_THRESH = 60
CARD_THRESH = 30

# Width and height of card corner, where rank and suit are
CORNER_WIDTH = 64
CORNER_HEIGHT = 160

# Dimensions of rank train images
RANK_WIDTH = 70
RANK_HEIGHT = 125

# Dimensions of suit train images
SUIT_WIDTH = 70
SUIT_HEIGHT = 100

RANK_DIFF_MAX = 4000
SUIT_DIFF_MAX = 2000

CARD_MAX_AREA = 120000
CARD_MIN_AREA = 25000

font = cv2.FONT_HERSHEY_SIMPLEX

# Structures to hold query card and train card information
class Query_card:
    def __init__(self):
        self.contour = []
        self.width, self.height = 0, 0
        self.corner_pts = []
        self.center = []
        self.warp = []
        self.rank_img = []
        self.suit_img = []
        self.best_rank_match = "Unknown"
        self.best_suit_match = "Unknown"
        self.rank_diff = 0
        self.suit_diff = 0

class Train_ranks:
    def __init__(self):
        self.img = None
        self.name = "Placeholder"

class Train_suits:
    def __init__(self):
        self.img = None
        self.name = "Placeholder"

def load_ranks(filepath):
    train_ranks = []
    i = 0
    # Change Rank Ace, Two... To Ace1, Ace2, Ace3, Two1, Two2, Two3...
    # for Rank in ["Ace1", "Ace2", "Ace3", "Two1", "Two2", "Two3", "Three1", "Three2", "Three3", "Four1", "Four2", "Four3", "Five1", "Five2", "Five3", "Six1", "Six2", "Six3", "Seven1", "Seven2", "Seven3", "Eight1", "Eight2", "Eight3", "Nine1", "Nine2", "Nine3", "Ten1", "Ten2", "Ten3", "Jack1", "Jack2", "Jack3", "Queen1", "Queen2", "Queen3", "King1", "King2", "King3"]:
    for Rank in ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven",
              "Eight", "Nine", "Ten", "Jack", "Queen", "King"]:
        train_ranks.append(Train_ranks())
        train_ranks[i].name = Rank
        filename = filepath + Rank + '.jpg'
        train_ranks[i].img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
        i += 1

    return train_ranks

def load_suits(filepath):
    train_suits = []
    i = 0
    for Suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']:
        train_suits.append(Train_suits())
        train_suits[i].name = Suit
        filename = filepath + Suit + '.jpg'
        train_suits[i].img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
        i += 1

    print("Suits loaded")
    return train_suits

# Function to preprocess image
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    img_w, img_h = np.shape(image)[:2]
    bkg_level = blur[int(img_h / 100)][int(img_w / 2)]
    thresh_level = bkg_level + BKG_THRESH # Threshold level to binary threshold the image
    retval, thresh = cv2.threshold(blur, thresh_level, 255, cv2.THRESH_BINARY)

    return thresh

# Function to find contours and sort them by area
def find_cards(thresh_image):
    cnts, hier = cv2.findContours(thresh_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    index_sort = sorted(range(len(cnts)), key=lambda i: cv2.contourArea(cnts[i]), reverse=True)

    if len(cnts) == 0:
        return [], []

    cnts_sort = []
    hier_sort = []
    cnt_is_card = np.zeros(len(cnts), dtype=int)

    for i in index_sort:
        cnts_sort.append(cnts[i])
        hier_sort.append(hier[0][i])

    for i in range(len(cnts_sort)):
        size = cv2.contourArea(cnts_sort[i])
        peri = cv2.arcLength(cnts_sort[i], True)
        approx = cv2.approxPolyDP(cnts_sort[i], 0.01 * peri, True)

        if ((size < CARD_MAX_AREA) and (size > CARD_MIN_AREA) and (hier_sort[i][3] == -1) and (len(approx) == 4)):
            cnt_is_card[i] = 1

    return cnts_sort, cnt_is_card

def preprocess_card(contour, image):
    qCard = Query_card()
    qCard.contour = contour
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.01 * peri, True)

    pts = np.float32(approx)
    s = pts.sum(axis=2)
    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]
    diff = np.diff(pts, axis=-1)
    tr = pts[np.argmin(diff)]
    bl = pts[np.argmax(diff)]

    if tl[0][0] > 10:
        qCard.corner_pts = [tl, tr, br, bl]

    qCard.width, qCard.height = find_card_dimensions(qCard.corner_pts)

    qCard.center = find_card_center(qCard.corner_pts)

    qCard.warp = flattener(image, qCard.corner_pts, qCard.width, qCard.height)

    Qcorner = qCard.warp[0:CORNER_HEIGHT, 0:CORNER_WIDTH]
    Qcorner_zoom = cv2.resize(Qcorner, (0, 0), fx=2.5, fy=2.5)

    white_level = Qcorner_zoom[15,int((CORNER_WIDTH*4)/2)]
    # white_level = Qcorner_zoom[15, 15]
    thresh_level = white_level - CARD_THRESH
    if isinstance(thresh_level, np.ndarray):
        thresh_level = thresh_level[0]
    if thresh_level <= 0:
        thresh_level = 1

    # Convert to grayscale
    gray_corner = cv2.cvtColor(Qcorner_zoom, cv2.COLOR_BGR2GRAY)
    # remove noise
    blur_corner = cv2.GaussianBlur(gray_corner, (5, 5), 0)
    # apply binary threshold
    retval, thresh_corner = cv2.threshold(blur_corner, 155, 255, cv2.THRESH_BINARY)

    Qrank_roi = thresh_corner[20:215, 0:130] # [y1:y2, x1:x2]
    Qsuit_roi = thresh_corner[225:460, 0:142]
    Qrank_cnts, hier = cv2.findContours(Qrank_roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    Qrank_cnts = sorted(Qrank_cnts, key=cv2.contourArea, reverse=True)

    # DEBUG:
    # cv2.imshow("Rank", Qrank_roi)
    # cv2.imshow("Suit", Qsuit_roi)

    if len(Qrank_cnts) != 0:
        x, y, w, h = cv2.boundingRect(Qrank_cnts[0])
        Qrank = Qrank_roi[y:y + h, x:x + w]
        qCard.rank_img = cv2.resize(Qrank, (RANK_WIDTH, RANK_HEIGHT), 0, 0)

    Qsuit_cnts, hier = cv2.findContours(Qsuit_roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    Qsuit_cnts = sorted(Qsuit_cnts, key=cv2.contourArea, reverse=True)
    if len(Qsuit_cnts) != 0:
        x, y, w, h = cv2.boundingRect(Qsuit_cnts[0])
        Qsuit = Qsuit_roi[y:y + h, x:x + w]
        qCard.suit_img = cv2.resize(Qsuit, (SUIT_WIDTH, SUIT_HEIGHT), 0, 0)

    return qCard

# Function to call the match_card function for each card in the image
def match_card(qCard, train_ranks, train_suits):
    best_rank_match_diff = 10000
    best_suit_match_diff = 10000
    best_rank_match_name = "Unknown"
    best_suit_match_name = "Unknown"

    # Invert colors (white card, black symbols)
    qCard.rank_img = cv2.bitwise_not(qCard.rank_img)
    cv2.imshow("Rank", qCard.rank_img)
    qCard.suit_img = cv2.bitwise_not(qCard.suit_img)

    if (len(qCard.rank_img) != 0) and (len(qCard.suit_img) != 0):
        # Test 6 in train_ranks
        cv2.imshow("IMG", train_ranks[5].img)
        for Trank in train_ranks:
            diff_img = cv2.absdiff(qCard.rank_img, Trank.img)
            rank_diff = int(np.sum(diff_img) / 255)
            if rank_diff < best_rank_match_diff:
                best_rank_match_diff = rank_diff
                best_rank_name = Trank.name

        for Tsuit in train_suits:
            diff_img = cv2.absdiff(qCard.suit_img, Tsuit.img)
            suit_diff = int(np.sum(diff_img) / 255)
            if suit_diff < best_suit_match_diff:
                best_suit_match_diff = suit_diff
                best_suit_name = Tsuit.name

        # Only consider matches below a certain difference threshold  
        if best_rank_match_diff < RANK_DIFF_MAX:
            best_rank_match_name = best_rank_name
        if best_suit_match_diff < SUIT_DIFF_MAX:
            best_suit_match_name = best_suit_name

    return best_rank_match_name, best_suit_match_name, best_rank_match_diff, best_suit_match_diff

def draw_results(image, qCard):
    x = qCard.center[0]
    y = qCard.center[1]
    cv2.putText(image, (qCard.best_rank_match+" of"), (x-60, y-10), font, 0.7, (0,255,0), 2, cv2.LINE_AA)
    cv2.putText(image, qCard.best_suit_match, (x-60, y+20), font, 0.7, (0,255,0), 2, cv2.LINE_AA)
    return image

def find_card_dimensions(corner_pts):
    width = np.sqrt(((corner_pts[0][0][0] - corner_pts[1][0][0])**2) + ((corner_pts[0][0][1] - corner_pts[1][0][1])**2))
    height = np.sqrt(((corner_pts[0][0][0] - corner_pts[3][0][0])**2) + ((corner_pts[0][0][1] - corner_pts[3][0][1])**2))
    return int(width), int(height)

def find_card_center(corner_pts):
    center_x = int((corner_pts[0][0][0] + corner_pts[2][0][0]) / 2)
    center_y = int((corner_pts[0][0][1] + corner_pts[2][0][1]) / 2)
    return center_x, center_y

def flattener(image, corner_pts, width, height):
    tmp_rect = np.zeros((4, 2), dtype="float32")
    s = np.sum(corner_pts, axis=2)
    diff = np.diff(corner_pts, axis= -1)
    tmp_rect[0] = corner_pts[np.argmin(s)]
    tmp_rect[2] = corner_pts[np.argmax(s)]
    tmp_rect[1] = corner_pts[np.argmin(diff)]
    tmp_rect[3] = corner_pts[np.argmax(diff)]
    maxWidth = width
    maxHeight = height
    dst = np.array([[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(tmp_rect, dst)
    warp = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warp
