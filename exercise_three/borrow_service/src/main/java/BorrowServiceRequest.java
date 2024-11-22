public class BorrowServiceRequest {

    String studentId;
    String bookId;
    String dateReturned;

    public BorrowServiceRequest(String studentId, String bookId, String dateReturned) {
        this.studentId      =   studentId;
        this.bookId         =   bookId;
        this.dateReturned   =   dateReturned;
    }
}
