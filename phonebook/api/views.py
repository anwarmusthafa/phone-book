from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer, UserSerializer, ContactSerializer, SpamReportSerializer
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, Contact, SpamReport, GlobalDatabase
from django.db.models import Count, Q


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        print(request.user)
        return Response({"message": "Hello World!"}, status=status.HTTP_200_OK)


class AddContactView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ContactSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            try:
                contact = serializer.save()
                return Response(ContactSerializer(contact).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SpamReportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SpamReportSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SearchByNameView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, name):
        try:
        
            starts_with_query = GlobalDatabase.objects.filter(name__istartswith=name)
            
           
            contains_query = GlobalDatabase.objects.filter(
                Q(name__icontains=name) & ~Q(name__istartswith=name)
            )

            
            results = list(starts_with_query) + list(contains_query)

            
            response_data = []
            for result in results:
                spam_reports_count = SpamReport.objects.filter(phone_number=result.phone_number).count()
                
                response_data.append({
                    "name": result.name,
                    "phone_number": result.phone_number,
                    "spam_reports_count": spam_reports_count 
                })

            return Response(response_data, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=400)
        

class SearchByPhoneNumberView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, phone_number):
        try:
            
            registered_user = CustomUser.objects.filter(phone_number=phone_number).first()
            
            response_data = []

            if registered_user:
                
                is_in_contact_list = Contact.objects.filter(user=request.user, phone_number=phone_number).exists()

                response_data.append({
                    "name": registered_user.name,
                    "phone_number": registered_user.phone_number,
                    "email": registered_user.email if is_in_contact_list else None,
                    "spam_reports_count": SpamReport.objects.filter(phone_number=phone_number).count(),
                })
            else:
                
                global_results = GlobalDatabase.objects.filter(phone_number=phone_number)

                for result in global_results:
                    response_data.append({
                        "name": result.name,
                        "phone_number": result.phone_number,
                        "spam_reports_count": SpamReport.objects.filter(phone_number=phone_number).count(),
                    })

            return Response(response_data, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=400)
    

