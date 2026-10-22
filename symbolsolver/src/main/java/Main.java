import com.github.javaparser.ast.CompilationUnit;
import constants.Constants;
import graph.entities.MyClassDTO;
import parser.Parse;
import parser.Parser;
import projects.MetricsCalculator;

import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

public class Main {

    public static void main(String[] args) throws IOException {

        if (System.getProperty("parse") != null) {
            parseProject(Constants.PROJECT_PATH);
        } else if (System.getProperty("metrics") != null) {
            runMetrics();
        }
    }

    public static Map<String, MyClassDTO> parseProject(String projectPath) throws IOException {
        Parser parser = new Parser();
        List<CompilationUnit> compilationUnits = parser.parseProject(Path.of(projectPath));

        // TODO : Consider merging Parse with Parser
        Parse parse = new Parse();
        return parse.completeParse(compilationUnits);
    }

    public static void runMetrics() {
        MetricsCalculator metricsCalculator = new MetricsCalculator();
        metricsCalculator.calculate();

    }

}
