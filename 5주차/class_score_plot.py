import matplotlib.pyplot as plt

def read_data(filename):
    data = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            if not line.startswith('#'): # If 'line' is not a header
                data.append([int(word) for word in line.split(',')])
    return data

if __name__ == '__main__':
    # Load score data
    class_kr = read_data('data/class_score_kr.csv')
    class_en = read_data('data/class_score_en.csv')

    # TODO) Prepare midterm, final, and total scores
    midterm_kr, final_kr = zip(*class_kr)
    total_kr = [40/125*midterm + 60/100*final for (midterm, final) in class_kr]
    midterm_en, final_en = zip(*class_en)
    total_en = [40/125*midterm + 60/100*final for (midterm, final) in class_en]

    # TODO) Plot midterm/final scores as points
    plt.figure()
    plt.scatter(midterm_kr, final_kr, label='Korean', marker='o', color='red')
    plt.scatter(midterm_en, final_en, label='English', marker='+', color='blue')
    plt.xlim(0, 125)
    plt.ylim(0, 100)
    plt.grid(True)
    plt.xlabel('Midterm scores')
    plt.ylabel('Final scores')
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig('class_score_scatter.png', dpi=150)

    # TODO) Plot total scores as a histogram
    plt.figure()
    plt.hist(total_kr, bins=range(0, 101, 5), color='red', alpha=1, label='Korean')
    plt.hist(total_en, bins=range(0, 101, 5), color='slateblue', alpha=0.3, label='English')
    plt.xlim(0, 100)
    plt.xlabel('Total scores')
    plt.ylabel('The number of students')
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig('class_score_hist.png', dpi=150)

    plt.show()