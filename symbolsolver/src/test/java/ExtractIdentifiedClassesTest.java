import com.github.javaparser.ast.CompilationUnit;
import extraction.ExtractIdentifiedClasses;
import graph.entities.MyClass;
import org.junit.jupiter.api.Test;
import parser.Parse;
import parser.Parser;

import java.io.*;
import java.nio.file.Path;
import java.util.*;



public class ExtractIdentifiedClassesTest {


    @Test
    public void parseAndExtractBulk() throws IOException {
        Set<String> repos = new HashSet<>();
        String path = "/home/mbrito/git/thesis/githubextraction/extra_projects.csv";
        // Get all the repos
        try (BufferedReader reader = new BufferedReader(new FileReader(path))) {
            String line = reader.readLine();
            while (line != null) {
                repos.add(line);
                line = reader.readLine();
            }

        } catch (IOException e) {
            e.printStackTrace();
        }

        for(String repo : repos){
            repo = repo.split(",")[0];
            System.out.println("Found repo: " + repo);
            parseAndExtract(repo);
        }

    }


    public void parseAndExtract(String projectName) throws IOException {
        projectName = projectName.replace("/", "__");
        String path = "/home/mbrito/git/thesis-web-applications/monoliths/" + projectName;
        String dstFolder = "/home/mbrito/git/thesis/data/interfaces";


        Parser parser = new Parser();
        List<CompilationUnit> compilationUnits = parser.parseProject(Path.of(path));

        Parse parse = new Parse();
        Map<String, MyClass> parseResult = parse.extractClasses(compilationUnits);


        //System.out.println(parseResult.keySet().toString());

        List<String> filters = Arrays.asList("(?i)\\.*controller$");
        ExtractIdentifiedClasses extract = new ExtractIdentifiedClasses();
        List<String> classes = extract.extractFilterBased(new ArrayList<>(parseResult.keySet()), filters);
        classes.forEach(System.out::println);

        try(BufferedWriter bf = new BufferedWriter(new FileWriter(dstFolder + "/" + projectName))){
            for (String classe : classes) {
                bf.write(classe + "\n");
            }
        } catch (IOException e){
            e.printStackTrace();
        }

    }

}
