import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

import com.rabbitmq.client.AMQP;
import com.rabbitmq.client.Consumer;
import com.rabbitmq.client.Envelope;
import com.rabbitmq.client.ShutdownSignalException;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;

public class BorrowService implements Consumer {
    private final static String POSTGRES_USER = System.getenv("POSTGRES_USER");
    private final static String POSTGRES_PASSWORD = System.getenv("POSTGRES_PASSWORD");
    private final static String POSTGRES_DB = System.getenv("POSTGRES_DB");
    private final static String POSTGRES_HOST = System.getenv("POSTGRES_HOST");
    private final static String POSTGRES_PORT = System.getenv("POSTGRES_PORT");

    private Connection databaseConnection;

    public BorrowService() {
        this.databaseConnection = createDatabaseConnection();
    }


    @Override
    public void handleDelivery(String consumerTag, Envelope envelope,
            AMQP.BasicProperties properties, byte[] body) throws UnsupportedEncodingException {

        try {
            String message = new String(body, "UTF-8");
            System.out.println(" [x] Received '" + message + "'");

            String userServiceHost = System.getenv("USER_SERVICE_HOST");
            String userServicePort = System.getenv("USER_SERVICE_PORT");
            String bookServiceHost = System.getenv("BOOK_SERVICE_HOST");
            String bookServicePort = System.getenv("BOOK_SERVICE_PORT");

            if (userServiceHost == null)
                userServiceHost = "localhost";
            if (userServicePort == null)
                userServicePort = "5002";
            if (bookServiceHost == null)
                bookServiceHost = "localhost";
            if (bookServicePort == null)
                bookServicePort = "5006";

            BorrowServiceRequest borrowServiceRequest = createBorrowServiceRequest(message);

            String users = new String(
                    "http://" + userServiceHost + ":" + userServicePort + "/users/"
                            + borrowServiceRequest.studentId);

            String books = new String(
                    "http://" + bookServiceHost + ":" + bookServicePort + "/books/"
                            + borrowServiceRequest.bookId);

            if (checkUser(users) && checkBook(books)) {
                this.databaseConnection.createStatement().executeUpdate(
                        "INSERT INTO borrowed_books VALUES ('" + borrowServiceRequest.studentId
                                + "', '" + borrowServiceRequest.bookId + "', '"
                                + borrowServiceRequest.dateReturned + "');");
            }

        } catch (Exception e) {
            e.printStackTrace();
        }

    }

    private Connection createDatabaseConnection() {
        Connection connection = null;
        try {
            connection = DriverManager.getConnection(
                    "jdbc:postgresql://" + POSTGRES_HOST + ":" + POSTGRES_PORT
                            + "/" + POSTGRES_DB,
                    POSTGRES_USER, POSTGRES_PASSWORD);
            Statement statement = connection.createStatement();

            // Check if the table exists
            ResultSet resultSet = statement.executeQuery(
                    "SELECT EXISTS (" +
                            "SELECT FROM information_schema.tables " +
                            "WHERE table_schema = 'public' " +
                            "AND table_name = 'borrowed_books'" +
                            ");");

            if (resultSet.next() && !resultSet.getBoolean(1)) {
                // Create the table if it doesn't exist
                statement.executeUpdate(
                        "CREATE TABLE borrowed_books (" +
                                "studentId VARCHAR(255) NOT NULL, " +
                                "bookId VARCHAR(255) NOT NULL, " +
                                "date_returned DATE NOT NULL, " +
                                "PRIMARY KEY (studentId, bookId)" +
                                ");");
                System.out.println("Table 'borrowed_books' created successfully.");
            } else {
                System.out.println("Table 'borrowed_books' already exists.");
            }

        } catch (Exception e) {
            e.printStackTrace();
        }

        return connection;
    }
    private BorrowServiceRequest createBorrowServiceRequest(String message) throws JsonProcessingException {
        try {
            JsonNode jsonNode = new ObjectMapper().readTree(message);
            String studentId = jsonNode.get("studentid").asText();
            String bookId = jsonNode.get("bookid").asText();
            String dateReturned = jsonNode.get("date_returned").asText();

            return new BorrowServiceRequest(studentId, bookId, dateReturned);

        } catch (JsonProcessingException e) {
            e.printStackTrace();
            return null;
        }
    }

    private boolean checkUser(String studentId) {

        // check user exists
        try {
            URL url = new URL(studentId);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setDoOutput(true);

            if (connection.getResponseCode() != 200) return false;

        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }

        // check user has no more than 5 books borrowed already
        try {
            Statement statement = this.databaseConnection.createStatement();
            ResultSet resultSet = statement.executeQuery(
                    "SELECT COUNT(*) FROM borrowed_books WHERE studentId = '" + studentId + "';");
            resultSet.next();
            int count = resultSet.getInt(1);
            if (count < 5) return true;
            else return false;

        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }

    }

    private boolean checkBook(String bookId) {
        // check book exists
        try {
            URL url = new URL(bookId);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setDoOutput(true);

            if (connection.getResponseCode() != 200) return false;

        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }

        // check book is not borrowed
        try {
            Statement statement = this.databaseConnection.createStatement();
            ResultSet resultSet = statement.executeQuery(
                    "SELECT COUNT(*) FROM borrowed_books WHERE bookId = '" + bookId + "';");
            resultSet.next();
            int count = resultSet.getInt(1);
            if (count == 0) return true;
            else return false;

        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }

    @Override
    public void handleConsumeOk(String consumerTag) {
        System.out.println(" [*] Waiting for messages. To exit press Ctrl+C");
    }

    @Override
    public void handleCancelOk(String consumerTag) {
    }

    @Override
    public void handleCancel(String consumerTag) {
    }

    @Override
    public void handleShutdownSignal(String consumerTag, ShutdownSignalException sig) {
    }

    @Override
    public void handleRecoverOk(String consumerTag) {
    }

}
