import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
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
            String borrowServiceHost = System.getenv("BORROW_SERVICE_HOST");

            if (userServiceHost == null)
                userServiceHost = "localhost";
            if (userServicePort == null)
                userServicePort = "5002";

            BorrowServiceRequest borrowServiceRequest = createBorrowServiceRequest(message);

            String users = new String(
                    "http://" + userServiceHost + ":" + userServicePort + "/users/"
                            + borrowServiceRequest.studentId);

            String books = new String(
                    "http://" + userServiceHost + ":" + userServicePort + "/books/"
                            + borrowServiceRequest.bookId);

            if (checkIdIntegrity(users) && checkIdIntegrity(books)) {
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
                                "user_id VARCHAR(255) NOT NULL, " +
                                "book_id VARCHAR(255) NOT NULL, " +
                                "borrow_date DATE NOT NULL, " +
                                "PRIMARY KEY (user_id, book_id)" +
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

    private boolean checkIdIntegrity(String urlString) {
        try {
            URL url = new URL(urlString);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setDoOutput(true);

            if (connection.getResponseCode() == 200) {
                return true;
            } else {
                System.out.println(
                        "GET request to " + url + " service failed with response code: "
                                + connection.getResponseCode());
                return false;
            }

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
