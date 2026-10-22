package graph.entities;

import com.github.javaparser.ast.body.MethodDeclaration;
import com.google.gson.annotations.Expose;
import constants.Constants;

import java.util.*;
import java.util.stream.Collectors;


public class MyMethod {
    private MyClass myClass;
    @Expose
    private String name;
    @Expose
    private List<String> parametersDataType;
    @Expose
    private List<String> returnDataType;
    private MethodDeclaration visitor;

    // TODO : Add myClass as parent on constructors
    public MyMethod(String name) {
        this.name = name;
        this.parametersDataType = new ArrayList<>();
    }

    public String getName() {
        return name;
    }

    public List<String> getParametersDataType() {
        return parametersDataType;
    }

    public void setParametersDataType(List<String> parametersDataType) {
        this.parametersDataType = parametersDataType.stream().filter(s -> !Constants.STOP_WORDS_DATA_TYPES.contains(s.toLowerCase())).collect(Collectors.toList());
    }

    public void setReturnDataType(List<String> returnDataType) {
        this.returnDataType = returnDataType.stream().filter(s -> !Constants.STOP_WORDS_DATA_TYPES.contains(s.toLowerCase())).collect(Collectors.toList());
    }

    public MyClass getMyClass() {
        return myClass;
    }

    public void setVisitor(MethodDeclaration visitor) {
        this.visitor = visitor;
    }

    public MethodDeclaration getVisitor() {
        return visitor;
    }

    public void setMyClass(MyClass myClass) {
        if (myClass.getMethods().containsKey(name)) {
            this.myClass = myClass;
        }
    }

    @Override
    public String toString() {
        return "MyMethod{" +
                "parametersDataType=" + parametersDataType +
                ", returnDataType='" + returnDataType + '\'' +
                '}';
    }
}
