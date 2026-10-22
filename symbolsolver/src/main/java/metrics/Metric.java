package metrics;

import java.io.IOException;

public interface Metric {
    double calculateService() throws IOException;
}
