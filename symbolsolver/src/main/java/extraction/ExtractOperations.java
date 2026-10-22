package extraction;

import com.github.javaparser.ast.body.MethodDeclaration;
import graph.entities.MyClass;
import graph.entities.Service;
import parser.ParseResultServices;

import java.util.*;

public class ExtractOperations {

    public static void extractAtServiceLevelInterfaces(ParseResultServices parseResultServices, Set<String> interfaces) {
        Map<Integer, Service> services = parseResultServices.getServices();

        for (Map.Entry<Integer, Service> service : services.entrySet()) {
            for (Map.Entry<String, MyClass> classe : service.getValue().getClasses().entrySet()) {
                // We found an interface, get the operations
                if (interfaces.contains(classe.getKey())) {
                    for (MethodDeclaration md : classe.getValue().getVisitor().findAll(MethodDeclaration.class)) {
                        String methodName = md.getNameAsString();

                        classe.getValue().getOperations().add(methodName);
                    }
                }
            }
        }
    }

    public static void mapServices(Map<Integer, Service> services) {
        for (Service service : services.values()) {
            Map<String, String> operations = new HashMap<>();
            for (MyClass source : service.getClasses().values()) {
                for (String op : source.getOperations()) {
                    operations.put(op, source.getQualifiedName());
                }
            }
            service.setOperations(operations);
        }
    }
}
