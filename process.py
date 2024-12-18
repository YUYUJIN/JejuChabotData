from code import process_search_data
from code import process_recommend_data
from code import reviews_to_vectors
from code import make_vector_store

def main():
    process_search_data()
    reviews_to_vectors()
    process_recommend_data()
    make_vector_store()

if __name__=='__main__':
    main()