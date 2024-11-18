import java.io.UnsupportedEncodingException;

import com.rabbitmq.client.AMQP;
import com.rabbitmq.client.Consumer;
import com.rabbitmq.client.Envelope;
import com.rabbitmq.client.ShutdownSignalException;

public class BorrowService implements Consumer {
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

    @Override
    public void handleDelivery(String consumerTag, Envelope envelope, 
                                AMQP.BasicProperties properties, byte[] body
                                ) throws UnsupportedEncodingException {
        String message = new String(body, "UTF-8");
        System.out.println(" [x] Received '" + message + "'");
    }
}
