import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.Connection;

import java.io.IOException;
import java.util.concurrent.CountDownLatch;

import com.rabbitmq.client.Channel;

public class Main {
    private final static String QUEUE_NAME = "borrow_request";

    public static void main(String[] argv) throws Exception {

        ConnectionFactory factory = new ConnectionFactory();
        String host = System.getenv("RABBITMQ_HOST");

        host = host == null ? "localhost" : host;
        System.out.println("RABBITMQ_HOST: " + host);

        factory.setHost(host);

        try (Connection connection = factory.newConnection();
            Channel channel = connection.createChannel()) {
            channel.queueDeclare(QUEUE_NAME, false, false, false, null);

            BorrowService borrowService = new BorrowService();
            channel.basicConsume(QUEUE_NAME, true, borrowService);

            CountDownLatch latch = new CountDownLatch(1);
            latch.await();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}